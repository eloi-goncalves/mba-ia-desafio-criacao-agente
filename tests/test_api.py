"""Testes de contrato da API que não dependem do modelo (sem GOOGLE_API_KEY).

Os fluxos de conversa que acionam o modelo são validados pelo avaliador com a
chave dele; aqui cobrimos criação de sessão, 404, 409 e rotas de verificação.
"""

from __future__ import annotations

import importlib

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client(tmp_path, monkeypatch):
    from app import config

    monkeypatch.setattr(config, "VAR_DIR", tmp_path)
    monkeypatch.setattr(config, "CONDOMINIO_DB", tmp_path / "condominio.db")
    monkeypatch.setattr(config, "SESSOES_DB", tmp_path / "sessoes.db")
    monkeypatch.setattr(
        config, "SESSION_DB_URL", f"sqlite+aiosqlite:///{tmp_path / 'sessoes.db'}"
    )

    from app import storage

    importlib.reload(storage)
    storage.restaurar_estado_inicial()

    import app.runtime as runtime

    importlib.reload(runtime)
    import app.api as api

    importlib.reload(api)

    transport = ASGITransport(app=api.app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_criar_sessao_retorna_201_e_session_id(client):
    r = await client.post("/sessoes", json={"apartamento": "101"})
    assert r.status_code == 201
    assert "session_id" in r.json() and r.json()["session_id"]


async def test_verificacao_reservas_101(client):
    r = await client.get("/apartamentos/101/reservas")
    assert r.status_code == 200
    assert {"codigo": "RSV-1377", "area": "quadra", "data": "2030-03-09"} in r.json()


async def test_verificacao_visitantes_302(client):
    r = await client.get("/apartamentos/302/visitantes")
    assert r.status_code == 200
    assert {"nome": "Marina Duarte", "data": "2030-03-16"} in r.json()


async def test_eventos_sessao_inexistente_404(client):
    r = await client.get("/sessoes/sessao-inexistente/eventos")
    assert r.status_code == 404


async def test_mensagem_sessao_inexistente_404(client):
    r = await client.post("/sessoes/sessao-inexistente/mensagens", json={"texto": "oi"})
    assert r.status_code == 404


async def test_confirmacao_id_inexistente_409(client):
    criado = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = criado.json()["session_id"]

    r = await client.post(
        f"/sessoes/{session_id}/confirmacoes",
        json={"id": "id-inexistente", "confirmado": True},
    )
    assert r.status_code == 409
    # Nada mudou nas reservas do 101.
    reservas = (await client.get("/apartamentos/101/reservas")).json()
    assert {"codigo": "RSV-1377", "area": "quadra", "data": "2030-03-09"} in reservas


async def test_confirmacao_sessao_inexistente_404(client):
    r = await client.post(
        "/sessoes/sessao-inexistente/confirmacoes",
        json={"id": "x", "confirmado": True},
    )
    assert r.status_code == 404


async def test_eventos_de_sessao_nova_vazios(client):
    criado = await client.post("/sessoes", json={"apartamento": "101"})
    session_id = criado.json()["session_id"]
    r = await client.get(f"/sessoes/{session_id}/eventos")
    assert r.status_code == 200
    assert r.json() == []
