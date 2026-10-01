"""Pruebas de normalización, intención y recuperación del conocimiento UPTx."""

from pathlib import Path

from retriever import UPTxRetriever, load_chunks, normalize
from tools import consultar_fuente_uptx


KNOWLEDGE = Path(__file__).parents[1] / "knowledge" / "uptx.md"


def test_normalize_removes_accents() -> None:
    """La consulta debe comparar palabras aunque tengan acentos."""

    assert normalize("Ingeniería química") == ["ingenieria", "quimica"]


def test_knowledge_is_split_into_chunks() -> None:
    """El Markdown debe convertirse en varias secciones consultables."""

    chunks = load_chunks(KNOWLEDGE)
    assert len(chunks) > 5
    assert any("Oferta educativa" in chunk.heading for chunk in chunks)


def test_retriever_finds_regulation_periods() -> None:
    """Las preguntas sobre ciclos encuentran el contenido normativo."""

    results = UPTxRetriever(KNOWLEDGE).search("¿Cuántos cuatrimestres hay por ciclo escolar?")
    assert results
    assert any("cuatrimestr" in result.text.lower() for result in results)


def test_retriever_finds_offer_for_careers() -> None:
    """Las preguntas sobre carreras priorizan la oferta educativa."""

    results = UPTxRetriever(KNOWLEDGE).search("¿Qué carreras ofrece la UPTx?")
    assert results
    assert results[0].heading == "Oferta educativa"
    assert "Ingeniería Mecatrónica" in results[0].text


def test_retriever_finds_article_10() -> None:
    """La pregunta sobre doble inscripción encuentra el artículo correcto."""

    results = UPTxRetriever(KNOWLEDGE).search("¿Puedo estar inscrito en dos programas académicos?")
    assert results
    assert "simultáneamente" in results[0].text
    assert results[0].heading == "Admisión e inscripción"


def test_retriever_returns_empty_for_unknown_question() -> None:
    """Una pregunta fuera del alcance no debe producir contexto inventado."""

    assert UPTxRetriever(KNOWLEDGE).search("¿Cuál es el menú de la cafetería?") == []


def test_retriever_does_not_repeat_headings() -> None:
    """La respuesta no debe repetir la misma sección del Markdown."""

    results = UPTxRetriever(KNOWLEDGE).search("reglamento derechos obligaciones sanciones")
    headings = [result.heading for result in results]
    assert len(headings) == len(set(headings))


def test_source_tool_extracts_relevant_official_page(monkeypatch) -> None:
    """La tool visita una fuente UPTx y devuelve el texto relevante."""

    class FakeResponse:
        url = "https://uptlax.edu.mx/becas-3/"
        headers = {"content-type": "text/html; charset=utf-8"}
        text = """
        <html><body><main>
          <h1>Becas UPTx</h1>
          <p>La universidad publica convocatorias de becas.</p>
          <p>Consulta requisitos y fechas en la fuente oficial.</p>
        </main></body></html>
        """

        def raise_for_status(self):
            return None

    monkeypatch.setattr("tools.requests.get", lambda *args, **kwargs: FakeResponse())

    result = consultar_fuente_uptx(
        "https://uptlax.edu.mx/becas-3/",
        "¿Qué requisitos tienen las becas?",
    )

    assert "Fuente consultada: https://uptlax.edu.mx/becas-3/" in result
    assert "requisitos" in result


def test_source_tool_rejects_non_official_url() -> None:
    """La tool no debe convertirse en un navegador de cualquier dominio."""

    result = consultar_fuente_uptx("https://example.com/private")

    assert "dominio" in result
    assert "no consulté" in result.lower()
