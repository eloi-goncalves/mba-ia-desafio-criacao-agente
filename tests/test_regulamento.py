"""Testes do recuperador do regulamento (Garantia 4)."""

from __future__ import annotations

from app import regulamento


def test_piscina_domingo_traz_horario_de_fechamento():
    trecho = regulamento.buscar("Até que horas a piscina funciona aos domingos?")
    assert "20h" in trecho
    assert "piscina" in trecho.lower()


def test_nao_retorna_regulamento_inteiro():
    trecho = regulamento.buscar("Até que horas a piscina funciona aos domingos?")
    # Não deve arrastar capítulos de outros assuntos (ex.: lixo/resíduos, academia).
    assert "óleo de cozinha" not in trecho.lower()
    assert "academia" not in trecho.lower()


def test_sem_correspondencia_retorna_vazio():
    assert regulamento.buscar("xyzzy termo inexistente qwerty") == ""
