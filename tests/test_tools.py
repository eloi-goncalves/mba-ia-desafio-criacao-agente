"""Testes das tools com um ToolContext de teste (sem depender do modelo)."""

from __future__ import annotations

import importlib

import pytest


class ConfirmacaoFake:
    def __init__(self, confirmed: bool):
        self.confirmed = confirmed
        self.hint = ""
        self.payload = None


class ToolContextFake:
    """Dublê do ToolContext do ADK: carrega state e registra pedidos de confirmação."""

    def __init__(self, apartamento: str, tool_confirmation=None):
        self.state = {"apartamento": apartamento}
        self.tool_confirmation = tool_confirmation
        self.pedidos: list[dict] = []

    def request_confirmation(self, *, hint=None, payload=None):
        self.pedidos.append({"hint": hint, "payload": payload})


@pytest.fixture
def tools(tmp_path, monkeypatch):
    from app import config

    monkeypatch.setattr(config, "VAR_DIR", tmp_path)
    monkeypatch.setattr(config, "CONDOMINIO_DB", tmp_path / "condominio.db")

    from app import storage as storage_mod

    importlib.reload(storage_mod)
    storage_mod.restaurar_estado_inicial()

    from app import tools as tools_mod

    importlib.reload(tools_mod)
    return tools_mod


def test_apartamento_vem_da_sessao(tools):
    ctx = ToolContextFake("101")
    resultado = tools.consultar_minhas_reservas(ctx)
    assert {"codigo": "RSV-1377", "area": "quadra", "data": "2030-03-09"} in resultado["reservas"]


def test_nao_vaza_dados_de_outro_apartamento(tools):
    # Uma sessão do 101 nunca enxerga as reservas do 302 por estas tools.
    ctx = ToolContextFake("101")
    reservas = tools.consultar_minhas_reservas(ctx)["reservas"]
    assert all(r["codigo"] != "RSV-4821" for r in reservas)


def test_disponibilidade_so_informa_livre_ou_ocupada(tools):
    ctx = ToolContextFake("101")
    ocupada = tools.verificar_disponibilidade("salao-de-festas", "2030-03-16", ctx)
    assert ocupada["situacao"] == "ocupada"
    assert "RSV-4821" not in str(ocupada) and "302" not in str(ocupada)


def test_cancelar_so_afeta_proprio_apartamento(tools):
    # 101 tentando cancelar algo do 302 (salão 2030-03-16) não encontra nada.
    ctx = ToolContextFake("101")
    resultado = tools.cancelar_reserva("salao-de-festas", "2030-03-16", ctx)
    assert resultado["status"] == "nao_encontrada"


def test_reservar_area_sem_taxa_nao_pede_confirmacao(tools):
    ctx = ToolContextFake("101")
    resultado = tools.reservar_area("quadra", "2030-04-06", ctx)
    assert resultado["status"] == "reservada"
    assert ctx.pedidos == []


def test_reservar_area_com_taxa_pede_confirmacao(tools):
    ctx = ToolContextFake("101")
    resultado = tools.reservar_area("salao-de-festas", "2030-04-20", ctx)
    assert resultado["status"] == "pendente_confirmacao"
    assert ctx.pedidos and ctx.pedidos[0]["payload"]["area"] == "salao-de-festas"
    # Nada foi gravado antes da confirmação.
    assert tools.consultar_minhas_reservas(ctx)["reservas"] == [
        {"codigo": "RSV-1377", "area": "quadra", "data": "2030-03-09"}
    ]


def test_reservar_area_negada_nao_grava(tools):
    ctx = ToolContextFake("101", tool_confirmation=ConfirmacaoFake(confirmed=False))
    resultado = tools.reservar_area("salao-de-festas", "2030-04-20", ctx)
    assert resultado["status"] == "negada"


def test_reservar_area_confirmada_grava_uma_vez(tools):
    ctx = ToolContextFake("101", tool_confirmation=ConfirmacaoFake(confirmed=True))
    resultado = tools.reservar_area("salao-de-festas", "2030-04-20", ctx)
    assert resultado["status"] == "reservada"
    reservas = tools.consultar_minhas_reservas(ToolContextFake("101"))["reservas"]
    salao = [r for r in reservas if r["area"] == "salao-de-festas" and r["data"] == "2030-04-20"]
    assert len(salao) == 1


def test_autorizar_visitante_sempre_pede_confirmacao(tools):
    ctx = ToolContextFake("101")
    resultado = tools.autorizar_visitante("Joana Ribeiro", "2030-04-21", ctx)
    assert resultado["status"] == "pendente_confirmacao"
    assert ctx.pedidos[0]["payload"]["nome"] == "Joana Ribeiro"
    assert tools.consultar_meus_visitantes(ctx)["visitantes"] == []


def test_autorizar_visitante_confirmado_grava(tools):
    ctx = ToolContextFake("101", tool_confirmation=ConfirmacaoFake(confirmed=True))
    resultado = tools.autorizar_visitante("Joana Ribeiro", "2030-04-21", ctx)
    assert resultado["status"] == "autorizado"
    visitantes = tools.consultar_meus_visitantes(ToolContextFake("101"))["visitantes"]
    assert {"nome": "Joana Ribeiro", "data": "2030-04-21"} in visitantes
