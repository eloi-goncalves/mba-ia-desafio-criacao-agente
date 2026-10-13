"""Comando de restauração: repõe reservas e visitantes ao estado de dados/*.json.

As sessões do ADK (var/sessoes.db) NÃO são apagadas por este comando; apenas os
dados mutáveis do condomínio são restaurados. Para começar totalmente do zero,
remova o diretório var/.

Uso:
    uv run python -m scripts.restaurar
"""

from __future__ import annotations

from app import storage


def main() -> None:
    storage.restaurar_estado_inicial()
    print("Dados do condomínio restaurados ao estado inicial (dados/*.json).")


if __name__ == "__main__":
    main()
