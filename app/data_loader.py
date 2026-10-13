"""Carregamento somente-leitura do estado inicial do condomínio (dados/).

Estes arquivos são a fonte de verdade inicial e nunca são alterados em runtime.
As mudanças feitas pelo assistente vão para o armazenamento persistente (storage).
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from app import config


def _ler_json(caminho) -> Any:
    with open(caminho, encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_apartamentos() -> list[dict[str, str]]:
    """Lista de apartamentos, cada um com `numero` e `morador`."""
    return _ler_json(config.APARTAMENTOS_JSON)


def carregar_areas() -> list[dict[str, Any]]:
    """Lista de áreas comuns, cada uma com `id`, `nome` e `taxa`."""
    return _ler_json(config.AREAS_JSON)


def carregar_reservas() -> list[dict[str, str]]:
    """Reservas iniciais, cada uma com `codigo`, `apartamento`, `area` e `data`."""
    return _ler_json(config.RESERVAS_JSON)


def carregar_visitantes() -> list[dict[str, str]]:
    """Autorizações iniciais de visita, cada uma com `apartamento`, `nome` e `data`."""
    return _ler_json(config.VISITANTES_JSON)


def carregar_regulamento() -> str:
    """Texto completo do regulamento interno."""
    with open(config.REGULAMENTO_MD, encoding="utf-8") as arquivo:
        return arquivo.read()


@lru_cache(maxsize=1)
def mapa_apartamentos() -> dict[str, str]:
    """Mapa `numero -> morador` para validação rápida de apartamentos existentes."""
    return {a["numero"]: a["morador"] for a in carregar_apartamentos()}


@lru_cache(maxsize=1)
def mapa_areas() -> dict[str, dict[str, Any]]:
    """Mapa `id -> área` para consultar nome e taxa de cada área comum."""
    return {a["id"]: a for a in carregar_areas()}


def apartamento_existe(numero: str) -> bool:
    """Indica se o apartamento consta em dados/apartamentos.json."""
    return numero in mapa_apartamentos()


def area_existe(area_id: str) -> bool:
    """Indica se a área consta em dados/areas.json."""
    return area_id in mapa_areas()


def taxa_da_area(area_id: str) -> float | None:
    """Taxa da área (em reais) ou None se a área não existir."""
    area = mapa_areas().get(area_id)
    return None if area is None else float(area["taxa"])
