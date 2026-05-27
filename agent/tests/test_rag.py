"""Tests unitaires — rag/ (ingest, chunking, retrieve, reranker) — sans appels réseau ni ChromaDB réel."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path

from rag.ingest import RawPage, load_pdf, load_all_pdfs
from rag.chunking import Chunk, chunk_pages
from rag.retrieve import RetrievedChunk, retrieve, build_rag_context
from rag.reranker import rerank


# ══════════════════════════════════════════════════════════════════════════════
# ingest
# ══════════════════════════════════════════════════════════════════════════════

def _make_page(text: str, page: int = 10, filename: str = "ISTQB_CTFL_Syllabus_v4.0.1.pdf") -> RawPage:
    return RawPage(
        content=text,
        metadata={"source": "ISTQB CTFL v4.0.1", "filename": filename, "page": page, "language": "en"},
    )


def test_load_pdf_missing_file(tmp_path):
    pages = load_pdf(tmp_path / "nonexistent.pdf")
    assert pages == []


def test_load_pdf_skips_early_pages(tmp_path):
    """Les pages < 9 (couverture, ToC) doivent être ignorées."""
    fake_pdf = MagicMock()
    fake_pdf.page_count = 15

    def fake_page(i):
        page = MagicMock()
        page.get_text.return_value = "x" * 200 if i >= 9 else "copyright notice"
        return page

    fake_pdf.__getitem__ = lambda self, i: fake_page(i)
    fake_pdf.close = MagicMock()

    pdf_path = tmp_path / "ISTQB_CTFL_Syllabus_v4.0.1.pdf"
    pdf_path.touch()

    with patch("rag.ingest.fitz.open", return_value=fake_pdf):
        pages = load_pdf(pdf_path)

    # Seules les pages >= 9 avec contenu suffisant doivent être retournées
    assert all(p.metadata["page"] > 9 for p in pages)


def test_load_all_pdfs_empty_dir(tmp_path):
    pages = load_all_pdfs(tmp_path)
    assert pages == []


def test_load_all_pdfs_missing_dir():
    pages = load_all_pdfs("/nonexistent/path")
    assert pages == []


def test_raw_page_metadata():
    page = _make_page("Equivalence Partitioning divides input data into partitions.")
    assert page.metadata["language"] == "en"
    assert page.metadata["source"] == "ISTQB CTFL v4.0.1"


# ══════════════════════════════════════════════════════════════════════════════
# chunking
# ══════════════════════════════════════════════════════════════════════════════

def test_chunk_pages_basic():
    pages = [_make_page("A" * 3000, page=10)]
    chunks = chunk_pages(pages)
    assert len(chunks) >= 2  # un texte de 3000 chars doit produire plusieurs chunks


def test_chunk_pages_propagates_metadata():
    pages = [_make_page("Test technique : Equivalence Partitioning." * 20, page=42)]
    chunks = chunk_pages(pages)
    assert all(c.metadata["page"] == 42 for c in chunks)
    assert all(c.metadata["language"] == "en" for c in chunks)
    assert all("chunk_index" in c.metadata for c in chunks)


def test_chunk_pages_empty_input():
    assert chunk_pages([]) == []


def test_chunk_pages_skips_empty_content():
    pages = [RawPage(content="   ", metadata={})]
    chunks = chunk_pages(pages)
    assert chunks == []


def test_chunk_pages_short_text_single_chunk():
    pages = [_make_page("Boundary Value Analysis.", page=5)]
    chunks = chunk_pages(pages)
    assert len(chunks) == 1
    assert "Boundary Value Analysis" in chunks[0].content


# ══════════════════════════════════════════════════════════════════════════════
# retrieve
# ══════════════════════════════════════════════════════════════════════════════

def _mock_store(results: list[tuple]):
    """Crée un mock de Chroma retournant des résultats prédéfinis."""
    store = MagicMock()
    store.similarity_search_with_relevance_scores.return_value = results
    collection = MagicMock()
    collection.count.return_value = 10  # simule une base peuplée
    store._collection = collection
    return store


def _make_doc(content: str, source: str = "ISTQB CTFL v4.0.1", page: int = 39, language: str = "en"):
    from langchain_core.documents import Document
    return Document(
        page_content=content,
        metadata={"source": source, "page": page, "language": language},
    )


def test_retrieve_returns_chunks_above_threshold():
    doc = _make_doc("Equivalence Partitioning divides data into valid and invalid classes.")
    mock_store = _mock_store([(doc, 0.22)])

    with patch("rag.retrieve.get_or_create_store", return_value=mock_store), \
         patch("rag.retrieve.is_indexed", return_value=True):
        chunks = retrieve("account creation email validation")

    assert len(chunks) == 1
    assert chunks[0].score == 0.22
    assert "Equivalence Partitioning" in chunks[0].content


def test_retrieve_filters_below_threshold():
    doc = _make_doc("Some vaguely related text.")
    mock_store = _mock_store([(doc, 0.05)])  # sous le seuil de 0.10

    with patch("rag.retrieve.get_or_create_store", return_value=mock_store), \
         patch("rag.retrieve.is_indexed", return_value=True):
        chunks = retrieve("account creation")

    assert chunks == []


def test_retrieve_empty_when_not_indexed():
    with patch("rag.retrieve.is_indexed", return_value=False):
        chunks = retrieve("any query")
    assert chunks == []


def test_retrieve_handles_store_error():
    mock_store = MagicMock()
    mock_store.similarity_search_with_relevance_scores.side_effect = Exception("ChromaDB error")
    mock_store._collection.count.return_value = 5

    with patch("rag.retrieve.get_or_create_store", return_value=mock_store), \
         patch("rag.retrieve.is_indexed", return_value=True):
        chunks = retrieve("query")

    assert chunks == []


def test_retrieve_multiple_results_sorted():
    docs = [
        (_make_doc("Boundary Value Analysis.", page=40), 0.22),
        (_make_doc("Decision Table Testing.", page=41), 0.18),
        (_make_doc("State Transition Testing.", page=42), 0.05),  # sous seuil 0.10
    ]
    mock_store = _mock_store(docs)

    with patch("rag.retrieve.get_or_create_store", return_value=mock_store), \
         patch("rag.retrieve.is_indexed", return_value=True):
        chunks = retrieve("password boundary validation")

    assert len(chunks) == 2
    assert chunks[0].score == 0.22
    assert chunks[1].score == 0.18


# ══════════════════════════════════════════════════════════════════════════════
# build_rag_context
# ══════════════════════════════════════════════════════════════════════════════

def test_build_rag_context_empty():
    assert build_rag_context([]) == ""


def test_build_rag_context_single_chunk():
    chunk = RetrievedChunk(
        content="Equivalence Partitioning divides inputs into classes.",
        score=0.88,
        source="ISTQB CTFL v4.0.1",
        page=39,
        language="en",
    )
    ctx = build_rag_context([chunk])
    assert "Equivalence Partitioning" in ctx
    assert "ISTQB CTFL v4.0.1" in ctx
    assert "p.39" in ctx
    assert "0.88" in ctx


def test_build_rag_context_multiple_chunks_separated():
    chunks = [
        RetrievedChunk("BVA.", 0.90, "ISTQB CTFL v4.0.1", 40, "en"),
        RetrievedChunk("Decision Tables.", 0.78, "ISTQB CTAL-TA v4.0 FR", 55, "fr"),
    ]
    ctx = build_rag_context(chunks)
    assert "---" in ctx
    assert "Source ISTQB 1" in ctx
    assert "Source ISTQB 2" in ctx


# ══════════════════════════════════════════════════════════════════════════════
# reranker
# ══════════════════════════════════════════════════════════════════════════════

def _make_chunk(content: str, score: float, page: int) -> RetrievedChunk:
    return RetrievedChunk(content=content, score=score, source="ISTQB CTFL v4.0.1", page=page, language="en")


def test_rerank_reorders_by_cross_encoder_score():
    """Le reranker doit mettre en tête le chunk jugé le plus pertinent par le cross-encoder."""
    chunks = [
        _make_chunk("Boundary Value Analysis tests boundary conditions.", 0.20, 40),
        _make_chunk("Equivalence Partitioning divides inputs into classes.", 0.18, 39),
        _make_chunk("Decision Table combines multiple conditions.", 0.15, 41),
    ]
    query = "email format validation equivalence partitioning"

    # Le cross-encoder prédit des scores : EP > BVA > DT pour cette query
    mock_ce = MagicMock()
    mock_ce.predict.return_value = [1.2, 3.5, 0.8]  # EP (index 1) a le score le plus haut

    with patch("rag.reranker._get_reranker", return_value=mock_ce):
        result = rerank(query, chunks)

    assert len(result) == 3
    # EP doit être en tête (score cross-encoder = 3.5)
    assert "Equivalence Partitioning" in result[0].content
    assert "Boundary Value" in result[1].content
    assert "Decision Table" in result[2].content


def test_rerank_single_chunk_unchanged():
    """Un seul chunk ne doit pas passer par le cross-encoder."""
    chunks = [_make_chunk("Only chunk.", 0.22, 39)]
    mock_ce = MagicMock()

    with patch("rag.reranker._get_reranker", return_value=mock_ce):
        result = rerank("any query", chunks)

    assert result == chunks
    mock_ce.predict.assert_not_called()


def test_rerank_empty_input():
    """Une liste vide retourne une liste vide."""
    result = rerank("any query", [])
    assert result == []


def test_rerank_preserves_original_scores():
    """Le reranker réordonne mais conserve les scores cosinus ChromaDB."""
    chunks = [
        _make_chunk("BVA content.", 0.22, 40),
        _make_chunk("EP content.", 0.18, 39),
    ]
    mock_ce = MagicMock()
    mock_ce.predict.return_value = [0.5, 2.0]  # EP premier

    with patch("rag.reranker._get_reranker", return_value=mock_ce):
        result = rerank("query", chunks)

    # Scores ChromaDB inchangés
    assert result[0].score == 0.18  # EP (maintenant en tête)
    assert result[1].score == 0.22  # BVA (descendu)


def test_rerank_graceful_on_error():
    """Si le cross-encoder échoue, l'ordre original est conservé (pas de crash)."""
    chunks = [
        _make_chunk("BVA.", 0.22, 40),
        _make_chunk("EP.", 0.18, 39),
    ]
    mock_ce = MagicMock()
    mock_ce.predict.side_effect = RuntimeError("Model unavailable")

    with patch("rag.reranker._get_reranker", return_value=mock_ce):
        result = rerank("query", chunks)

    # Ordre original préservé
    assert result[0].content == "BVA."
    assert result[1].content == "EP."


def test_retrieve_calls_reranker_when_enabled():
    """retrieve() doit appeler le reranker quand RAG_RERANKER_ENABLED=True."""
    docs = [
        (_make_doc("BVA.", page=40), 0.22),
        (_make_doc("EP.", page=39), 0.18),
    ]
    mock_store = _mock_store(docs)
    rerank_mock = MagicMock(side_effect=lambda q, c: c)  # retourne les chunks inchangés

    with patch("rag.retrieve.get_or_create_store", return_value=mock_store), \
         patch("rag.retrieve.is_indexed", return_value=True), \
         patch("rag.retrieve.RAG_RERANKER_ENABLED", True), \
         patch("rag.reranker.rerank", rerank_mock):
        chunks = retrieve("boundary value email")

    rerank_mock.assert_called_once()


def test_retrieve_skips_reranker_when_disabled():
    """retrieve() ne doit PAS appeler le reranker quand RAG_RERANKER_ENABLED=False."""
    docs = [
        (_make_doc("BVA.", page=40), 0.22),
        (_make_doc("EP.", page=39), 0.18),
    ]
    mock_store = _mock_store(docs)
    rerank_mock = MagicMock()

    with patch("rag.retrieve.get_or_create_store", return_value=mock_store), \
         patch("rag.retrieve.is_indexed", return_value=True), \
         patch("rag.retrieve.RAG_RERANKER_ENABLED", False), \
         patch("rag.reranker.rerank", rerank_mock):
        chunks = retrieve("boundary value email")

    rerank_mock.assert_not_called()
