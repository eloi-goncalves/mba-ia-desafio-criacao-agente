"""Consulta sob demanda ao regulamento (Garantia 4).

O regulamento é longo. Em vez de carregá-lo inteiro no contexto, este módulo
recupera apenas o(s) trecho(s) relevante(s) para a pergunta, para que nenhum
evento da sessão carregue capítulos que tratam de outros assuntos.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

from app import data_loader

_STOPWORDS = {
    "a", "o", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "um", "uma",
    "que", "qual", "quais", "para", "por", "com", "no", "na", "nos", "nas", "ao",
    "aos", "se", "sua", "seu", "suas", "seus", "ou", "me", "minha", "meu", "ate",
    "quanto", "quantos", "como", "onde", "quando", "qual", "e", "ser", "sao", "pode",
    "posso", "ha", "sobre", "the",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def _tokens(texto: str) -> set[str]:
    palavras = re.findall(r"[a-z0-9]+", _normalizar(texto))
    return {p for p in palavras if len(p) > 2 and p not in _STOPWORDS}


@lru_cache(maxsize=1)
def _blocos() -> list[tuple[str, str]]:
    """Divide o regulamento em blocos por artigo, cada um com seu capítulo.

    Retorna uma lista de (capitulo, texto_do_bloco).
    """
    texto = data_loader.carregar_regulamento()
    linhas = texto.splitlines()
    blocos: list[tuple[str, str]] = []
    capitulo_atual = ""
    bloco_atual: list[str] = []

    def fechar() -> None:
        if bloco_atual:
            conteudo = "\n".join(bloco_atual).strip()
            if conteudo:
                blocos.append((capitulo_atual, conteudo))

    for linha in linhas:
        if linha.startswith("## "):
            fechar()
            bloco_atual = []
            capitulo_atual = linha.lstrip("# ").strip()
            continue
        if re.match(r"\*\*Art\. ", linha):
            fechar()
            bloco_atual = [linha]
            continue
        bloco_atual.append(linha)
    fechar()
    return blocos


def buscar(pergunta: str, limite: int = 1) -> str:
    """Retorna o(s) trecho(s) mais relevante(s) do regulamento para a pergunta.

    Nunca retorna o regulamento inteiro: apenas o(s) bloco(s) de maior pontuação,
    evitando levar capítulos de outros assuntos para a conversa (Garantia 4).
    """
    termos = _tokens(pergunta)
    if not termos:
        return ""

    pontuados: list[tuple[int, int, str, str]] = []
    for indice, (capitulo, conteudo) in enumerate(_blocos()):
        tokens_bloco = _tokens(f"{capitulo} {conteudo}")
        pontuacao = len(termos & tokens_bloco)
        if pontuacao > 0:
            pontuados.append((pontuacao, -indice, capitulo, conteudo))

    if not pontuados:
        return ""

    pontuados.sort(reverse=True)
    escolhidos = pontuados[: max(1, limite)]
    partes = [f"{capitulo}\n\n{conteudo}" for _, _, capitulo, conteudo in escolhidos]
    return "\n\n---\n\n".join(partes)
