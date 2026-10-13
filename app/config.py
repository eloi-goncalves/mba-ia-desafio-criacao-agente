"""Configuração central: caminhos, variáveis de ambiente e locais de armazenamento."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Raiz do repositório (dois níveis acima deste arquivo: app/config.py -> raiz).
RAIZ = Path(__file__).resolve().parent.parent

# Estado inicial imutável do condomínio (nunca é alterado em runtime).
DADOS_DIR = RAIZ / "dados"
APARTAMENTOS_JSON = DADOS_DIR / "apartamentos.json"
AREAS_JSON = DADOS_DIR / "areas.json"
RESERVAS_JSON = DADOS_DIR / "reservas.json"
VISITANTES_JSON = DADOS_DIR / "visitantes.json"
REGULAMENTO_MD = DADOS_DIR / "regulamento.md"

# Armazenamento persistente e mutável (fora de dados/, ignorado pelo Git).
VAR_DIR = RAIZ / "var"
CONDOMINIO_DB = VAR_DIR / "condominio.db"
SESSOES_DB = VAR_DIR / "sessoes.db"

# URL de sessão persistente do ADK (SQLite assíncrono), conforme dica oficial.
SESSION_DB_URL = f"sqlite+aiosqlite:///{SESSOES_DB}"

# Identificador da aplicação ADK.
APP_NAME = "assistente-aurora"

# Modelo Gemini usado pelos agentes (configurável; consulte os modelos e limites
# ativos no Google AI Studio). Pode ser sobrescrito por GEMINI_MODEL no .env.
MODELO_GEMINI = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def garantir_var_dir() -> None:
    """Cria o diretório de armazenamento local, se ainda não existir."""
    VAR_DIR.mkdir(parents=True, exist_ok=True)


def api_key_configurada() -> bool:
    """Indica se a chave do Google AI Studio está presente no ambiente."""
    return bool(os.getenv("GOOGLE_API_KEY"))
