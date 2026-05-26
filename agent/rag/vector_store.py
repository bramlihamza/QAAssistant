"""
rag/vector_store.py — Gestion de la base vectorielle ChromaDB.

Fournit :
  - get_or_create_store() : ouvre ou crée la collection ChromaDB persistante.
  - index_chunks()        : indexe une liste de Chunk (idempotent par ID).
  - is_indexed()          : vérifie si la base est déjà peuplée.
"""

import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
)
from rag.chunking import Chunk

logger = logging.getLogger(__name__)

# ── Singleton de l'instance Chroma ────────────────────────────────────────────
_store: Chroma | None = None


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model=EMBEDDING_MODEL,
    )


def get_or_create_store() -> Chroma:
    """
    Retourne l'instance Chroma (singleton).
    Crée la collection si elle n'existe pas encore.
    """
    global _store
    if _store is not None:
        return _store

    persist_dir = str(Path(CHROMA_PERSIST_DIR).resolve())
    logger.info(
        "Initialisation ChromaDB — collection='%s', persist_dir='%s'",
        CHROMA_COLLECTION, persist_dir,
    )

    _store = Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=_get_embeddings(),
        persist_directory=persist_dir,
        collection_metadata={"hnsw:space": "cosine"},  # scores dans [0, 1]
    )
    return _store


def is_indexed() -> bool:
    """
    Retourne True si la collection contient déjà des documents.
    Permet d'éviter une ré-ingestion inutile.
    """
    try:
        store = get_or_create_store()
        count = store._collection.count()
        logger.info("Collection '%s' : %d documents indexés.", CHROMA_COLLECTION, count)
        return count > 0
    except Exception as e:
        logger.warning("Impossible de vérifier l'index : %s", e)
        return False


def index_chunks(chunks: list[Chunk]) -> int:
    """
    Indexe une liste de chunks dans ChromaDB.

    L'ID de chaque chunk est construit à partir de la source + page + chunk_index
    pour garantir l'idempotence (pas de doublons si on ré-indexe).

    Args:
        chunks: liste de Chunk issus de rag/chunking.py

    Returns:
        Nombre de chunks effectivement indexés.
    """
    if not chunks:
        logger.warning("Aucun chunk à indexer.")
        return 0

    store = get_or_create_store()

    texts = [c.content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    ids = [
        f"{c.metadata.get('filename', 'doc')}_p{c.metadata.get('page', 0)}_c{c.metadata.get('chunk_index', 0)}"
        for c in chunks
    ]

    logger.info("Indexation de %d chunks en cours...", len(chunks))
    store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    logger.info("✅ %d chunks indexés dans la collection '%s'.", len(chunks), CHROMA_COLLECTION)

    return len(chunks)


def reset_store() -> None:
    """
    Supprime et recrée la collection (pour ré-ingestion propre).
    Nécessaire pour changer les paramètres de distance ou les documents source.
    """
    global _store
    persist_dir = str(Path(CHROMA_PERSIST_DIR).resolve())

    # Supprimer la collection via le client ChromaDB bas niveau
    import chromadb
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        client.delete_collection(CHROMA_COLLECTION)
        logger.warning("Collection '%s' supprimée.", CHROMA_COLLECTION)
    except Exception:
        logger.info("Collection '%s' n'existait pas encore.", CHROMA_COLLECTION)

    _store = None
    logger.info("Prêt pour une nouvelle ingestion.")
