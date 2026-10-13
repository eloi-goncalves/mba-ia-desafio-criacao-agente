"""Testes da fundação: carregamento dos dados e armazenamento persistente."""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def storage(tmp_path, monkeypatch):
    """Isola o banco de dados em um diretório temporário para cada teste."""
    from app import config

    monkeypatch.setattr(config, "VAR_DIR", tmp_path)
    monkeypatch.setattr(config, "CONDOMINIO_DB", tmp_path / "condominio.db")

    from app import storage as storage_mod

    importlib.reload(storage_mod)
    storage_mod.restaurar_estado_inicial()
    return storage_mod


def test_dados_iniciais_carregados(storage):
    reservas_101 = storage.listar_reservas("101")
    assert {"codigo": "RSV-1377", "area": "quadra", "data": "2030-03-09"} in reservas_101

    visitantes_302 = storage.listar_visitantes("302")
    assert {"nome": "Marina Duarte", "data": "2030-03-16"} in visitantes_302


def test_disponibilidade_nao_expoe_terceiros(storage):
    # 302 tem o salão reservado em 2030-03-16; a data está ocupada.
    assert storage.data_disponivel("salao-de-festas", "2030-03-16") is False
    assert storage.data_disponivel("salao-de-festas", "2030-04-20") is True


def test_criar_reserva_gera_codigo_unico(storage):
    codigo = storage.criar_reserva("101", "salao-de-festas", "2030-04-20")
    assert codigo is not None
    assert codigo.startswith("RSV-")
    assert codigo not in {"RSV-1377", "RSV-4821", "RSV-2950"}

    reservas = storage.listar_reservas("101")
    assert any(r["codigo"] == codigo for r in reservas)


def test_exclusividade_na_gravacao(storage):
    # Primeira reserva vence; a segunda para a mesma (área, data) é recusada.
    primeiro = storage.criar_reserva("101", "salao-de-festas", "2030-05-11")
    segundo = storage.criar_reserva("201", "salao-de-festas", "2030-05-11")
    assert primeiro is not None
    assert segundo is None

    total = len(storage.listar_reservas("101")) + len(storage.listar_reservas("201"))
    salao_0511 = [
        r
        for ap in ("101", "201")
        for r in storage.listar_reservas(ap)
        if r["area"] == "salao-de-festas" and r["data"] == "2030-05-11"
    ]
    assert len(salao_0511) == 1
    assert total >= 1


def test_cancelamento_so_afeta_proprio_apartamento(storage):
    # Tentar cancelar a reserva do 302 a partir do 101 não altera nada do 302.
    cancelados = storage.cancelar_reserva("101", "salao-de-festas", "2030-03-16")
    assert cancelados == []
    assert storage.listar_reservas("302") == [
        {"codigo": "RSV-4821", "area": "salao-de-festas", "data": "2030-03-16"}
    ]


def test_cancelar_propria_reserva(storage):
    cancelados = storage.cancelar_reserva("101", "quadra", "2030-03-09")
    assert cancelados == ["RSV-1377"]
    assert storage.listar_reservas("101") == []


def test_codigo_cancelado_nao_reaproveitado(storage):
    storage.cancelar_reserva("101", "quadra", "2030-03-09")
    novos = {
        storage.criar_reserva("101", "quadra", f"2030-06-{dia:02d}") for dia in range(1, 20)
    }
    assert "RSV-1377" not in novos


def test_autorizar_visitante(storage):
    storage.autorizar_visitante("101", "Joana Ribeiro", "2030-04-21")
    assert {"nome": "Joana Ribeiro", "data": "2030-04-21"} in storage.listar_visitantes("101")
