"""Armazenamento persistente e mutável do condomínio (reservas e visitantes).

Usa SQLite. A exclusividade de uma reserva por (área, data) é garantida por um
índice único parcial no banco — ou seja, no instante da gravação (Garantia 5),
não apenas por uma conferência prévia. Reservas canceladas permanecem na tabela
(coluna `ativa = 0`), de modo que seus códigos nunca são reaproveitados
(regra de negócio 5).
"""

from __future__ import annotations

import secrets
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app import config, data_loader


@contextmanager
def _conectar() -> Iterator[sqlite3.Connection]:
    """Abre uma conexão SQLite com chaves estrangeiras e row factory por nome."""
    config.garantir_var_dir()
    conexao = sqlite3.connect(config.CONDOMINIO_DB, isolation_level=None, timeout=10)
    conexao.row_factory = sqlite3.Row
    try:
        conexao.execute("PRAGMA journal_mode = WAL")
        conexao.execute("PRAGMA foreign_keys = ON")
        conexao.execute("PRAGMA busy_timeout = 5000")
        yield conexao
    finally:
        conexao.close()


def inicializar() -> None:
    """Cria as tabelas e o índice de exclusividade, se ainda não existirem."""
    with _conectar() as conexao:
        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS reservas (
                codigo      TEXT PRIMARY KEY,
                apartamento TEXT NOT NULL,
                area        TEXT NOT NULL,
                data        TEXT NOT NULL,
                ativa       INTEGER NOT NULL DEFAULT 1
            );

            -- Exclusividade no instante da gravação: no máximo uma reserva ATIVA
            -- por (área, data). Canceladas (ativa = 0) não ocupam a agenda.
            CREATE UNIQUE INDEX IF NOT EXISTS idx_reserva_unica_ativa
                ON reservas (area, data)
                WHERE ativa = 1;

            CREATE TABLE IF NOT EXISTS visitantes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                apartamento TEXT NOT NULL,
                nome        TEXT NOT NULL,
                data        TEXT NOT NULL
            );
            """
        )


def restaurar_estado_inicial() -> None:
    """Repõe reservas e visitantes ao estado de dados/*.json (comando de restauração)."""
    inicializar()
    with _conectar() as conexao:
        conexao.execute("BEGIN")
        conexao.execute("DELETE FROM reservas")
        conexao.execute("DELETE FROM visitantes")
        conexao.execute("DELETE FROM sqlite_sequence WHERE name = 'visitantes'")
        for reserva in data_loader.carregar_reservas():
            conexao.execute(
                "INSERT INTO reservas (codigo, apartamento, area, data, ativa) "
                "VALUES (?, ?, ?, ?, 1)",
                (reserva["codigo"], reserva["apartamento"], reserva["area"], reserva["data"]),
            )
        for visitante in data_loader.carregar_visitantes():
            conexao.execute(
                "INSERT INTO visitantes (apartamento, nome, data) VALUES (?, ?, ?)",
                (visitante["apartamento"], visitante["nome"], visitante["data"]),
            )
        conexao.execute("COMMIT")


# --- Consultas -----------------------------------------------------------------

def listar_reservas(apartamento: str) -> list[dict[str, str]]:
    """Reservas ATIVAS de um apartamento, no formato das rotas de verificação."""
    with _conectar() as conexao:
        linhas = conexao.execute(
            "SELECT codigo, area, data FROM reservas "
            "WHERE apartamento = ? AND ativa = 1 ORDER BY data, codigo",
            (apartamento,),
        ).fetchall()
    return [dict(linha) for linha in linhas]


def listar_visitantes(apartamento: str) -> list[dict[str, str]]:
    """Autorizações de visita de um apartamento, no formato das rotas de verificação."""
    with _conectar() as conexao:
        linhas = conexao.execute(
            "SELECT nome, data FROM visitantes WHERE apartamento = ? ORDER BY data, nome",
            (apartamento,),
        ).fetchall()
    return [dict(linha) for linha in linhas]


def data_disponivel(area: str, data: str) -> bool:
    """Indica se (área, data) está livre — sem expor de quem é a reserva (Garantia 2)."""
    with _conectar() as conexao:
        linha = conexao.execute(
            "SELECT 1 FROM reservas WHERE area = ? AND data = ? AND ativa = 1 LIMIT 1",
            (area, data),
        ).fetchone()
    return linha is None


# --- Escritas ------------------------------------------------------------------

def _gerar_codigo(conexao: sqlite3.Connection) -> str:
    """Gera um código RSV único, nunca repetindo nenhum código já existente."""
    while True:
        candidato = f"RSV-{secrets.randbelow(9000) + 1000}"
        existe = conexao.execute(
            "SELECT 1 FROM reservas WHERE codigo = ? LIMIT 1", (candidato,)
        ).fetchone()
        if existe is None:
            return candidato


def criar_reserva(apartamento: str, area: str, data: str) -> str | None:
    """Cria uma reserva ativa de forma atômica.

    Retorna o código gerado, ou None quando (área, data) já está ocupada —
    a exclusividade é imposta pelo índice único no instante da gravação (Garantia 5).
    """
    with _conectar() as conexao:
        try:
            conexao.execute("BEGIN IMMEDIATE")
            codigo = _gerar_codigo(conexao)
            conexao.execute(
                "INSERT INTO reservas (codigo, apartamento, area, data, ativa) "
                "VALUES (?, ?, ?, ?, 1)",
                (codigo, apartamento, area, data),
            )
            conexao.execute("COMMIT")
            return codigo
        except sqlite3.IntegrityError:
            conexao.execute("ROLLBACK")
            return None


def cancelar_reserva(apartamento: str, area: str, data: str) -> list[str]:
    """Cancela reservas ATIVAS do próprio apartamento que casem com (área, data).

    Retorna os códigos cancelados. Só afeta o apartamento informado (Garantia 2).
    """
    with _conectar() as conexao:
        conexao.execute("BEGIN IMMEDIATE")
        linhas = conexao.execute(
            "SELECT codigo FROM reservas "
            "WHERE apartamento = ? AND area = ? AND data = ? AND ativa = 1",
            (apartamento, area, data),
        ).fetchall()
        codigos = [linha["codigo"] for linha in linhas]
        if codigos:
            conexao.execute(
                "UPDATE reservas SET ativa = 0 "
                "WHERE apartamento = ? AND area = ? AND data = ? AND ativa = 1",
                (apartamento, area, data),
            )
        conexao.execute("COMMIT")
    return codigos


def autorizar_visitante(apartamento: str, nome: str, data: str) -> None:
    """Registra uma autorização de visita para o apartamento informado."""
    with _conectar() as conexao:
        conexao.execute(
            "INSERT INTO visitantes (apartamento, nome, data) VALUES (?, ?, ?)",
            (apartamento, nome, data),
        )
