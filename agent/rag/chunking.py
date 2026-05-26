"""
rag/chunking.py — Découpage des pages ISTQB en chunks optimisés pour le retrieval.

Stratégie :
  - RecursiveCharacterTextSplitter (LangChain) avec séparateurs hiérarchiques.
  - chunk_size  = 1500 caractères (~375 tokens) : suffisant pour conserver le contexte
    d'une technique de test (ex : section complète sur l'Equivalence Partitioning).
  - chunk_overlap = 150 caractères : évite les coupures sur des définitions clés.
  - Les métadonnées de la page source sont propagées à chaque chunk.
"""

import logging
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.ingest import RawPage

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)


@dataclass
class Chunk:
    """Représente un fragment de document prêt à être indexé."""
    content: str
    metadata: dict = field(default_factory=dict)


def chunk_pages(pages: list[RawPage]) -> list[Chunk]:
    """
    Découpe une liste de pages en chunks indexables.

    Args:
        pages: pages extraites par rag/ingest.py

    Returns:
        Liste de Chunk avec contenu et métadonnées.
    """
    chunks: list[Chunk] = []

    for page in pages:
        if not page.content.strip():
            continue

        splits = _splitter.split_text(page.content)

        for i, text in enumerate(splits):
            if not text.strip():
                continue
            chunks.append(Chunk(
                content=text,
                metadata={
                    **page.metadata,
                    "chunk_index": i,
                    "chunk_count": len(splits),
                },
            ))

    logger.info(
        "Chunking : %d pages → %d chunks (size=%d, overlap=%d)",
        len(pages), len(chunks), CHUNK_SIZE, CHUNK_OVERLAP,
    )
    return chunks
