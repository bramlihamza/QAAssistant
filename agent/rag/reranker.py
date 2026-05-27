"""
rag/reranker.py — Reranking cross-encoder pour le pipeline RAG.

Un bi-encoder (ChromaDB) récupère les K chunks les plus proches en espace vectoriel
mais ne compare pas directement query ↔ passage. Le cross-encoder corrige cela :
il évalue chaque paire (query, chunk) individuellement — plus lent mais bien plus précis.

Modèle : cross-encoder/ms-marco-MiniLM-L-6-v2
  - ~90 Mo, téléchargé une seule fois dans le cache HuggingFace
  - Entraîné sur MS MARCO (passages de recherche web)
  - Inference CPU en ~50 ms pour 5 chunks
  - Scores = logits bruts (pas bornés à [0,1]) — utilisés uniquement pour le tri

Impact attendu sur context_precision RAGAS : +0.15 à +0.30 (meilleur ordonnancement).
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rag.retrieve import RetrievedChunk

logger = logging.getLogger(__name__)

_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_reranker = None  # singleton — chargé à la première utilisation


def _get_reranker():
    """Retourne le cross-encoder (chargé en lazy, une seule fois)."""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        logger.info("Chargement du cross-encoder '%s'…", _RERANKER_MODEL)
        _reranker = CrossEncoder(_RERANKER_MODEL)
        logger.info("✅ Cross-encoder prêt.")
    return _reranker


def rerank(query: str, chunks: list["RetrievedChunk"]) -> list["RetrievedChunk"]:
    """
    Reordonne les chunks par pertinence query↔passage via un cross-encoder.

    Les scores ChromaDB (cosinus) servent à filtrer ; les scores cross-encoder
    servent uniquement à trier. Le score d'origine (cosine) est conservé dans
    chaque chunk — seul l'ordre change.

    Args:
        query:  requête utilisateur ou query RAG construite depuis les US.
        chunks: chunks récupérés par ChromaDB (déjà filtrés par seuil).

    Returns:
        Même liste, triée par score cross-encoder décroissant.
    """
    if len(chunks) <= 1:
        return chunks

    try:
        ce = _get_reranker()
        pairs = [(query, c.content) for c in chunks]
        ce_scores = ce.predict(pairs)

        # Zip (chunk, ce_score) et trier par score décroissant
        ranked = sorted(zip(chunks, ce_scores), key=lambda x: float(x[1]), reverse=True)
        reranked = [chunk for chunk, _ in ranked]

        logger.info(
            "Reranking : %d chunks réordonnés (top=%s, score_ce=%.3f)",
            len(reranked),
            reranked[0].source + " p." + str(reranked[0].page),
            float(ce_scores[list(chunks).index(reranked[0])]) if reranked else 0,
        )
        return reranked

    except Exception as e:
        logger.warning("Reranking échoué, ordre original conservé : %s", e)
        return chunks
