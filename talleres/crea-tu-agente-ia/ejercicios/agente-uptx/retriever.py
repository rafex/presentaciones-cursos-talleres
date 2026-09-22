"""Recuperación local y ligera de fragmentos del conocimiento UPTx."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

STOPWORDS = {
    "a",
    "al",
    "con",
    "cuál",
    "cual",
    "cómo",
    "como",
    "de",
    "del",
    "el",
    "en",
    "es",
    "la",
    "las",
    "los",
    "me",
    "para",
    "por",
    "qué",
    "que",
    "se",
    "su",
    "un",
    "una",
    "y",
}


@dataclass(frozen=True)
class Chunk:
    """Fragmento recuperable con su encabezado y contenido."""

    heading: str
    text: str


def normalize(text: str) -> list[str]:
    """Devuelve tokens comparables sin acentos ni puntuación."""

    plain = unicodedata.normalize("NFKD", text)
    plain = "".join(char for char in plain if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]+", plain.lower())


def load_chunks(path: Path) -> list[Chunk]:
    """Carga el Markdown y lo divide por encabezados y párrafos."""

    content = path.read_text(encoding="utf-8")
    chunks: list[Chunk] = []
    heading = "Información UPTx"
    paragraphs: list[str] = []

    def flush() -> None:
        if paragraphs:
            text = "\n\n".join(paragraphs).strip()
            if text:
                chunks.append(Chunk(heading=heading, text=text))
            paragraphs.clear()

    for line in content.splitlines():
        if line.startswith("#"):
            flush()
            heading = line.lstrip("#").strip()
        elif line.strip():
            paragraphs.append(line.strip())

    flush()
    return chunks


class UPTxRetriever:
    """Buscador por coincidencia de términos, sin servicio externo."""

    def __init__(self, knowledge_path: Path) -> None:
        self.knowledge_path = knowledge_path
        self.chunks = load_chunks(knowledge_path)

    def search(self, question: str, limit: int = 3) -> list[Chunk]:
        """Devuelve los fragmentos más relacionados con la pregunta."""

        query = set(normalize(question)) - STOPWORDS
        if not query:
            return []

        scored: list[tuple[int, int, Chunk]] = []
        for index, chunk in enumerate(self.chunks):
            haystack = set(normalize(f"{chunk.heading} {chunk.text}")) - STOPWORDS
            overlap = len(query & haystack)
            if overlap:
                scored.append((overlap, -index, chunk))

        scored.sort(reverse=True, key=lambda item: (item[0], item[1]))
        return [chunk for _, _, chunk in scored[:limit]]
