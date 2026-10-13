"""Teste de concorrência da Garantia 5: dois moradores, uma reserva."""

from __future__ import annotations

import importlib
from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.fixture
def storage(tmp_path, monkeypatch):
    from app import config

    monkeypatch.setattr(config, "VAR_DIR", tmp_path)
    monkeypatch.setattr(config, "CONDOMINIO_DB", tmp_path / "condominio.db")

    from app import storage as storage_mod

    importlib.reload(storage_mod)
    storage_mod.restaurar_estado_inicial()
    return storage_mod


def test_disputa_simultanea_uma_reserva_vence(storage):
    area, data = "salao-de-festas", "2030-05-11"

    def reservar(apartamento: str):
        return storage.criar_reserva(apartamento, area, data)

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(reservar, "101")
        f2 = executor.submit(reservar, "201")
        resultados = [f1.result(), f2.result()]

    vencedores = [r for r in resultados if r is not None]
    assert len(vencedores) == 1  # exatamente uma vence; a outra é recusada

    ativas = [
        r
        for ap in ("101", "201")
        for r in storage.listar_reservas(ap)
        if r["area"] == area and r["data"] == data
    ]
    assert len(ativas) == 1  # nunca duas reservas ativas para a mesma área/data
