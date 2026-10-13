"""Tools do assistente: leem e gravam reservas e visitantes pelo armazenamento.

As regras críticas ficam aqui, no código — não no prompt. O apartamento usado
por toda tool vem SEMPRE do `state` da sessão (Garantia 2), nunca de um valor
escolhido pelo modelo. Ações que geram cobrança ou liberam acesso passam por
confirmação explícita do sistema (Garantia 1).
"""

from __future__ import annotations

from google.adk.tools import ToolContext

from app import data_loader, regulamento, storage

# Chave do apartamento autenticado no state da sessão.
CHAVE_APARTAMENTO = "apartamento"


def _apartamento(tool_context: ToolContext) -> str:
    """Lê o apartamento autenticado do state da sessão (fonte única da verdade)."""
    apartamento = tool_context.state.get(CHAVE_APARTAMENTO)
    if not apartamento:
        raise ValueError("Sessão sem apartamento autenticado no state.")
    return str(apartamento)


# --- Leitura (sem confirmação) -------------------------------------------------

def consultar_minhas_reservas(tool_context: ToolContext) -> dict:
    """Lista as reservas ativas do apartamento da sessão."""
    return {"reservas": storage.listar_reservas(_apartamento(tool_context))}


def consultar_meus_visitantes(tool_context: ToolContext) -> dict:
    """Lista as autorizações de visita do apartamento da sessão."""
    return {"visitantes": storage.listar_visitantes(_apartamento(tool_context))}


def verificar_disponibilidade(area: str, data: str, tool_context: ToolContext) -> dict:
    """Informa se uma área está livre numa data, sem revelar de quem é a reserva.

    Args:
        area: id da área comum (ex.: "salao-de-festas", "churrasqueira", "quadra").
        data: data no formato AAAA-MM-DD.
    """
    if not data_loader.area_existe(area):
        return {"status": "area_desconhecida", "area": area}
    livre = storage.data_disponivel(area, data)
    return {"area": area, "data": data, "situacao": "livre" if livre else "ocupada"}


# --- Escritas sem cobrança/acesso (sem confirmação) ----------------------------

def cancelar_reserva(area: str, data: str, tool_context: ToolContext) -> dict:
    """Cancela a reserva do próprio apartamento para (área, data). Sem confirmação.

    Args:
        area: id da área comum.
        data: data no formato AAAA-MM-DD.
    """
    codigos = storage.cancelar_reserva(_apartamento(tool_context), area, data)
    if codigos:
        return {"status": "cancelada", "codigos": codigos}
    return {"status": "nao_encontrada", "area": area, "data": data}


# --- Ações que geram cobrança ou liberam acesso (com confirmação) --------------

def reservar_area(area: str, data: str, tool_context: ToolContext) -> dict:
    """Reserva uma área para o apartamento da sessão.

    Área com taxa maior que zero gera cobrança e exige confirmação do sistema
    (Garantia 1). Área com taxa zero é reservada diretamente.

    Args:
        area: id da área comum.
        data: data no formato AAAA-MM-DD.
    """
    if not data_loader.area_existe(area):
        return {"status": "area_desconhecida", "area": area}

    taxa = data_loader.taxa_da_area(area) or 0.0
    if taxa > 0:
        confirmacao = tool_context.tool_confirmation
        if confirmacao is None:
            tool_context.request_confirmation(
                hint=(
                    f"Reservar a área '{area}' em {data} gera cobrança de "
                    f"R$ {taxa:.2f}. Confirme pela rota de confirmações."
                ),
                payload={"acao": "reservar_area", "area": area, "data": data, "taxa": taxa},
            )
            return {"status": "pendente_confirmacao", "area": area, "data": data}
        if not confirmacao.confirmed:
            return {"status": "negada", "area": area, "data": data}

    codigo = storage.criar_reserva(_apartamento(tool_context), area, data)
    if codigo is None:
        return {"status": "indisponivel", "area": area, "data": data}
    return {"status": "reservada", "codigo": codigo, "area": area, "data": data}


def autorizar_visitante(nome: str, data: str, tool_context: ToolContext) -> dict:
    """Autoriza a entrada de um visitante para o apartamento da sessão.

    Liberar acesso exige confirmação do sistema (Garantia 1), mesmo que o morador
    diga que "já confirmou" na conversa.

    Args:
        nome: nome do visitante.
        data: data da visita no formato AAAA-MM-DD.
    """
    confirmacao = tool_context.tool_confirmation
    if confirmacao is None:
        tool_context.request_confirmation(
            hint=(
                f"Autorizar a entrada de {nome} em {data} libera acesso ao prédio. "
                f"Confirme pela rota de confirmações."
            ),
            payload={"acao": "autorizar_visitante", "nome": nome, "data": data},
        )
        return {"status": "pendente_confirmacao", "nome": nome, "data": data}
    if not confirmacao.confirmed:
        return {"status": "negada", "nome": nome, "data": data}

    storage.autorizar_visitante(_apartamento(tool_context), nome, data)
    return {"status": "autorizado", "nome": nome, "data": data}


# --- Regulamento (consulta sob demanda) ----------------------------------------

def consultar_regulamento(pergunta: str, tool_context: ToolContext) -> dict:
    """Consulta o regulamento interno e retorna só o trecho relevante à pergunta.

    Args:
        pergunta: dúvida do morador sobre o regulamento.
    """
    trecho = regulamento.buscar(pergunta)
    if not trecho:
        return {"status": "sem_correspondencia"}
    return {"status": "ok", "trecho": trecho}
