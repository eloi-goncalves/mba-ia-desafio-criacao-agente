"""API HTTP do assistente do Residencial Aurora (contrato oficial do desafio).

As rotas de conversa passam pelo assistente ADK; as rotas de verificação leem os
dados do condomínio direto do armazenamento, sem passar pelo modelo.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app import runtime, storage

app = FastAPI(title="Assistente do Residencial Aurora")


class CriarSessaoIn(BaseModel):
    apartamento: str


class SessaoOut(BaseModel):
    session_id: str


class MensagemIn(BaseModel):
    texto: str


class ConfirmacaoIn(BaseModel):
    id: str
    confirmado: bool


@app.post("/sessoes", status_code=201, response_model=SessaoOut)
async def criar_sessao(corpo: CriarSessaoIn):
    session_id = await runtime.criar_sessao(corpo.apartamento)
    return {"session_id": session_id}


@app.post("/sessoes/{session_id}/mensagens")
async def enviar_mensagem(session_id: str, corpo: MensagemIn):
    if await runtime.obter_sessao(session_id) is None:
        raise HTTPException(status_code=404, detail="sessão não encontrada")

    resposta = await runtime.enviar_mensagem(session_id, corpo.texto)
    sessao = await runtime.obter_sessao(session_id)
    return {
        "resposta": resposta,
        "confirmacoes_pendentes": runtime.confirmacoes_pendentes(sessao),
    }


@app.post("/sessoes/{session_id}/confirmacoes")
async def responder_confirmacao(session_id: str, corpo: ConfirmacaoIn):
    sessao = await runtime.obter_sessao(session_id)
    if sessao is None:
        raise HTTPException(status_code=404, detail="sessão não encontrada")

    pendentes = {c["id"] for c in runtime.confirmacoes_pendentes(sessao)}
    if corpo.id not in pendentes:
        raise HTTPException(
            status_code=409, detail="não existe confirmação pendente com esse id nesta sessão"
        )

    resposta = await runtime.responder_confirmacao(session_id, corpo.id, corpo.confirmado)
    sessao = await runtime.obter_sessao(session_id)
    return {
        "resposta": resposta,
        "confirmacoes_pendentes": runtime.confirmacoes_pendentes(sessao),
    }


@app.get("/sessoes/{session_id}/eventos")
async def listar_eventos(session_id: str):
    sessao = await runtime.obter_sessao(session_id)
    if sessao is None:
        raise HTTPException(status_code=404, detail="sessão não encontrada")
    return runtime.serializar_eventos(sessao)


@app.get("/apartamentos/{numero}/reservas")
async def reservas_do_apartamento(numero: str):
    return storage.listar_reservas(numero)


@app.get("/apartamentos/{numero}/visitantes")
async def visitantes_do_apartamento(numero: str):
    return storage.listar_visitantes(numero)
