"""Runtime do assistente: SessionService persistente, Runner e helpers de execução.

A persistência de sessão usa SQLite (Garantia 3), conforme a dica oficial. O
apartamento autenticado é gravado no `state` da sessão na criação e consumido
pelas tools. As confirmações pendentes são derivadas dos eventos da sessão: uma
confirmação é "pendente" enquanto existir um function call `adk_request_confirmation`
sem a resposta correspondente — o que fornece naturalmente o `409` de reenvio.
"""

from __future__ import annotations

from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from app import config, storage
from app.agentes import root_agent

# Nome da função especial de confirmação do ADK.
_CONFIRMACAO = "adk_request_confirmation"

# user_id fixo: o contrato identifica a conversa apenas por session_id; o
# apartamento autenticado vive no state da sessão, não no user_id.
USER_ID = "morador"

# Inicialização idempotente do armazenamento e do diretório local.
config.garantir_var_dir()
storage.inicializar()

session_service = DatabaseSessionService(db_url=config.SESSION_DB_URL)
runner = Runner(
    app_name=config.APP_NAME,
    agent=root_agent,
    session_service=session_service,
)


async def criar_sessao(apartamento: str) -> str:
    """Cria uma sessão persistente com o apartamento autenticado no state."""
    sessao = await session_service.create_session(
        app_name=config.APP_NAME,
        user_id=USER_ID,
        state={"apartamento": apartamento},
    )
    return sessao.id


async def obter_sessao(session_id: str):
    """Retorna a sessão persistida ou None se não existir."""
    return await session_service.get_session(
        app_name=config.APP_NAME, user_id=USER_ID, session_id=session_id
    )


def _texto_do_evento(event) -> str:
    if not event.content or not event.content.parts:
        return ""
    partes = [p.text for p in event.content.parts if getattr(p, "text", None)]
    return "".join(partes)


async def _consumir(generator) -> str:
    """Executa o generator do Runner e devolve o texto da resposta final."""
    resposta = ""
    async for event in generator:
        if event.is_final_response():
            texto = _texto_do_evento(event)
            if texto:
                resposta = texto
    return resposta


async def enviar_mensagem(session_id: str, texto: str) -> str:
    """Envia uma mensagem do morador e retorna o texto da resposta final."""
    conteudo = types.Content(role="user", parts=[types.Part(text=texto)])
    return await _consumir(
        runner.run_async(user_id=USER_ID, session_id=session_id, new_message=conteudo)
    )


async def responder_confirmacao(session_id: str, confirmacao_id: str, confirmado: bool) -> str:
    """Responde uma confirmação pendente, retomando a execução da tool original."""
    resposta = types.FunctionResponse(
        id=confirmacao_id,
        name=_CONFIRMACAO,
        response={"confirmed": confirmado},
    )
    conteudo = types.Content(role="user", parts=[types.Part(function_response=resposta)])
    return await _consumir(
        runner.run_async(user_id=USER_ID, session_id=session_id, new_message=conteudo)
    )


def _como_dict(valor: Any) -> dict:
    if valor is None:
        return {}
    if isinstance(valor, dict):
        return valor
    return {}


def confirmacoes_pendentes(sessao) -> list[dict]:
    """Deriva as confirmações pendentes a partir dos eventos da sessão.

    Pendente = function call `adk_request_confirmation` sem resposta correspondente.
    """
    pedidos: dict[str, Any] = {}
    respondidas: set[str] = set()

    for event in sessao.events:
        for fc in event.get_function_calls() or []:
            if fc.name == _CONFIRMACAO:
                pedidos[fc.id] = fc
        for fr in event.get_function_responses() or []:
            if fr.name == _CONFIRMACAO and fr.id:
                respondidas.add(fr.id)

    pendentes: list[dict] = []
    for fc_id, fc in pedidos.items():
        if fc_id in respondidas:
            continue
        args = _como_dict(fc.args)
        tool_conf = _como_dict(args.get("toolConfirmation"))
        payload = _como_dict(tool_conf.get("payload"))
        original = _como_dict(args.get("originalFunctionCall"))
        acao = payload.get("acao") or original.get("name") or ""
        detalhes = {k: v for k, v in payload.items() if k != "acao"}
        pendentes.append({"id": fc_id, "acao": acao, "detalhes": detalhes})
    return pendentes


def serializar_eventos(sessao) -> list[dict]:
    """Serializa todos os eventos da sessão, em ordem, com conteúdo completo."""
    return [event.model_dump(mode="json", exclude_none=True) for event in sessao.events]
