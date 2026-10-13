"""Teste de fumaça: os agentes são construídos com a topologia esperada."""

from __future__ import annotations


def test_topologia_dos_agentes():
    from app import agentes

    root = agentes.root_agent
    assert root.name == "coordenador"

    nomes = {sub.name for sub in root.sub_agents}
    assert nomes == {
        "especialista_reservas",
        "especialista_visitantes",
        "especialista_regulamento",
    }
    # Pelo menos dois especialistas (requisito de arquitetura).
    assert len(root.sub_agents) >= 2


def test_principal_nao_recebe_regulamento_nas_instrucoes():
    from app import agentes, data_loader

    instrucao = agentes.coordenador.instruction
    # Nenhum trecho do regulamento vai nas instruções do agente principal (Garantia 4).
    assert "Art. 1º" not in instrucao
    assert "Capítulo" not in instrucao
    regulamento = data_loader.carregar_regulamento()
    assert regulamento[:200] not in instrucao
