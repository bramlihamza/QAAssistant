"""
scripts/ingest_docs.py — Script d'ingestion one-shot des PDFs ISTQB dans ChromaDB.

À exécuter UNE FOIS avant de démarrer l'agent (ou après mise à jour des PDFs).

Usage :
    uv run python scripts/ingest_docs.py
    uv run python scripts/ingest_docs.py --force   # ré-indexe même si déjà peuplé

Le script :
  1. Charge les PDFs depuis ISTQB_DOCS_DIR (config.py / .env).
  2. Découpe en chunks (1500 chars, overlap 150).
  3. Génère les embeddings via text-embedding-3-small (OpenAI).
  4. Stocke dans ChromaDB (CHROMA_PERSIST_DIR / CHROMA_COLLECTION).
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Assurer que le répertoire agent/ est dans le path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("ingest_docs")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingestion des PDFs ISTQB dans ChromaDB."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ré-indexer même si la base est déjà peuplée.",
    )
    args = parser.parse_args()

    # Import après ajout du path
    from config import ISTQB_DOCS_DIR, CHROMA_PERSIST_DIR, CHROMA_COLLECTION
    from rag.ingest import load_all_pdfs
    from rag.chunking import chunk_pages
    from rag.vector_store import is_indexed, index_chunks, reset_store

    logger.info("═" * 60)
    logger.info("QA Assistant — Ingestion ISTQB")
    logger.info("═" * 60)
    logger.info("Répertoire PDFs : %s", Path(ISTQB_DOCS_DIR).resolve())
    logger.info("ChromaDB       : %s / %s", CHROMA_PERSIST_DIR, CHROMA_COLLECTION)

    # Vérifier si déjà indexé
    if is_indexed() and not args.force:
        logger.info("✅ Base déjà indexée. Utilisez --force pour ré-indexer.")
        return

    if args.force:
        logger.warning("--force : réinitialisation de la collection...")
        reset_store()

    # 1. Chargement des PDFs
    t0 = time.time()
    docs_dir = Path(ISTQB_DOCS_DIR).resolve()
    pages = load_all_pdfs(docs_dir)

    if not pages:
        logger.error("❌ Aucune page extraite. Vérifiez ISTQB_DOCS_DIR dans .env")
        sys.exit(1)

    logger.info("📄 Pages chargées : %d", len(pages))

    # 2. Chunking
    chunks = chunk_pages(pages)
    logger.info("✂️  Chunks générés : %d", len(chunks))

    # 3. Indexation (génération embeddings + stockage ChromaDB)
    logger.info("⏳ Génération des embeddings et indexation ChromaDB...")
    logger.info("   (cela peut prendre 1–2 minutes selon la taille des documents)")

    count = index_chunks(chunks)

    elapsed = time.time() - t0
    logger.info("═" * 60)
    logger.info("✅ Ingestion terminée en %.1fs", elapsed)
    logger.info("   %d chunks indexés dans '%s'", count, CHROMA_COLLECTION)
    logger.info("═" * 60)


if __name__ == "__main__":
    main()
