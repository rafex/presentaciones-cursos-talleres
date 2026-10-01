"""Retriever local y ligero para el conocimiento institucional de la UPTx.

No usa embeddings, una base vectorial ni un servicio externo. Lee un Markdown
versionado, lo separa por encabezados y puntúa cada fragmento con coincidencias
de términos. Los encabezados pesan más que el cuerpo y las expansiones de
intención relacionan palabras como ``carreras`` e ``ingenierías``.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

# Términos que aparecen en casi cualquier pregunta institucional y no ayudan a
# distinguir la intención. Se conservan sólo los términos informativos.
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
    "ofrece",
    "ofrecer",
    "universidad",
    "politecnica",
    "tlaxcala",
    "uptx",
    "lista",
    "completa",
    "dame",
    "hay",
    "tiene",
    "tienen",
}

# Variantes y conceptos relacionados que mejoran la búsqueda sin incorporar
# una dependencia de NLP. Las claves y valores se normalizan sin acentos.
INTENT_EXPANSIONS = {
    "carrera": {"carreras", "oferta", "educativa", "programas", "ingenieria", "licenciatura"},
    "carreras": {"carrera", "oferta", "educativa", "programas", "ingenieria", "licenciatura"},
    "ingenieria": {"ingenierias", "carrera", "carreras", "oferta", "educativa", "programas"},
    "ingenierias": {"ingenieria", "carrera", "carreras", "oferta", "educativa", "programas"},
    "programa": {"programas", "carrera", "carreras", "oferta", "educativa"},
    "programas": {"programa", "carrera", "carreras", "oferta", "educativa"},
    "oferta": {"educativa", "carrera", "carreras", "programas", "ingenieria"},
    "reglamento": {"derechos", "obligaciones", "faltas", "sanciones", "articulo"},
    "derechos": {"reglamento", "alumnos", "examen", "calificaciones"},
    "obligaciones": {"reglamento", "alumnos", "asistir", "seguridad"},
    "sanciones": {"reglamento", "faltas", "baja", "expulsion"},
    "cuatrimestre": {"cuatrimestres", "ciclo", "escolar", "periodos", "cursos"},
    "cuatrimestres": {"cuatrimestre", "ciclo", "escolar", "periodos", "cursos"},
    "ciclo": {"escolar", "cuatrimestre", "cuatrimestres", "periodos", "cursos"},
    "cursos": {"curso", "cuatrimestre", "cuatrimestres", "ciclo", "escolar"},
    "calendario": {"escolar", "ciclo", "admision", "fechas", "inscripcion"},
}

# Estas señales ayudan a evitar que una pregunta normativa reciba primero la
# sección de oferta educativa sólo porque ambas mencionan a la universidad.
REGULATION_QUERY_TERMS = {
    "alumno",
    "articulo",
    "derechos",
    "inscrito",
    "inscripcion",
    "obligaciones",
    "reglamento",
    "simultaneamente",
    "sanciones",
}

# Señales de preguntas que sí deben priorizar la oferta académica.
OFFER_QUERY_TERMS = {
    "carrera",
    "carreras",
    "educativa",
    "ingenieria",
    "ingenierias",
    "licenciatura",
    "oferta",
}


@dataclass(frozen=True)
class Chunk:
    """Fragmento recuperable con el encabezado que le da contexto."""

    heading: str
    text: str


def normalize(text: str) -> list[str]:
    """Devuelve tokens comparables sin acentos, mayúsculas ni puntuación."""

    plain = unicodedata.normalize("NFKD", text)
    plain = "".join(char for char in plain if not unicodedata.combining(char))
    return re.findall(r"[a-z0-9]+", plain.lower())


def expand_query(question: str) -> set[str]:
    """Normaliza la pregunta y agrega términos de intención relacionados.

    Por ejemplo, ``carreras`` activa también ``oferta`` y ``programas``. Esto
    permite que una pregunta natural encuentre el encabezado oficial aunque no
    repita exactamente las mismas palabras.
    """

    tokens = set(normalize(question)) - STOPWORDS
    expanded = set(tokens)
    for token in tokens:
        expanded.update(INTENT_EXPANSIONS.get(token, set()))
    return expanded - STOPWORDS


def load_chunks(path: Path) -> list[Chunk]:
    """Carga el Markdown y lo divide por encabezados y párrafos.

    Cada encabezado inicia una sección. Los párrafos siguientes se agrupan en
    un ``Chunk`` hasta encontrar el siguiente encabezado. Así las respuestas
    pueden conservar el título y el contexto de la fuente.
    """

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
    """Buscador por coincidencia de términos, sin servicio externo.

    La puntuación favorece coincidencias en títulos, frases completas y
    vocabulario de la intención. ``search`` devuelve como máximo una sección
    por encabezado para no repetir la misma fuente en la respuesta.
    """

    def __init__(self, knowledge_path: Path) -> None:
        self.knowledge_path = knowledge_path
        self.chunks = load_chunks(knowledge_path)

    def search(self, question: str, limit: int = 3) -> list[Chunk]:
        """Devuelve los fragmentos más relacionados con la pregunta.

        Las preguntas sin términos informativos devuelven una lista vacía.
        También se aplica un filtro mínimo para que una coincidencia genérica
        no parezca una respuesta válida a una pregunta fuera del alcance.
        """

        raw_query = set(normalize(question)) - STOPWORDS
        query = expand_query(question)
        if not query:
            return []

        regulatory_intent = bool(raw_query & REGULATION_QUERY_TERMS)
        offer_intent = bool(raw_query & OFFER_QUERY_TERMS)

        scored: list[tuple[int, int, int, Chunk]] = []
        for index, chunk in enumerate(self.chunks):
            if regulatory_intent and not offer_intent and chunk.heading in {
                "Oferta educativa",
                "Fuentes oficiales",
            }:
                continue
            heading_tokens = set(normalize(chunk.heading)) - STOPWORDS
            body_tokens = set(normalize(chunk.text)) - STOPWORDS
            heading_overlap = len(query & heading_tokens)
            body_overlap = len(query & body_tokens)
            normalized_question = " ".join(normalize(question))
            normalized_heading = " ".join(normalize(chunk.heading))
            phrase_bonus = 4 if normalized_heading and normalized_heading in normalized_question else 0
            regulation_bonus = 0
            if query & REGULATION_QUERY_TERMS and (
                "reglamento" in heading_tokens or "inscripcion" in heading_tokens
            ):
                regulation_bonus = 8
            # El título identifica mejor la intención que una mención aislada
            # dentro del texto. La frase exacta y el reglamento reciben bonos.
            score = (heading_overlap * 4) + body_overlap + phrase_bonus + regulation_bonus
            if score >= 2:
                scored.append((score, heading_overlap, -index, chunk))

        scored.sort(reverse=True, key=lambda item: (item[0], item[1], item[2]))
        selected: list[Chunk] = []
        seen_headings: set[str] = set()
        for _, _, _, chunk in scored:
            if chunk.heading not in seen_headings:
                selected.append(chunk)
                seen_headings.add(chunk.heading)
            if len(selected) == limit:
                break
        return selected
