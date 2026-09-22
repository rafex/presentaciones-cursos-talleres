from pathlib import Path

from retriever import UPTxRetriever, load_chunks, normalize


KNOWLEDGE = Path(__file__).parents[1] / "knowledge" / "uptx.md"


def test_normalize_removes_accents() -> None:
    assert normalize("Ingeniería química") == ["ingenieria", "quimica"]


def test_knowledge_is_split_into_chunks() -> None:
    chunks = load_chunks(KNOWLEDGE)
    assert len(chunks) > 5
    assert any("Oferta educativa" in chunk.heading for chunk in chunks)


def test_retriever_finds_regulation_periods() -> None:
    results = UPTxRetriever(KNOWLEDGE).search("¿Cuántos cuatrimestres hay por ciclo escolar?")
    assert results
    assert any("cuatrimestr" in result.text.lower() for result in results)


def test_retriever_returns_empty_for_unknown_question() -> None:
    assert UPTxRetriever(KNOWLEDGE).search("¿Cuál es el menú de la cafetería?") == []
