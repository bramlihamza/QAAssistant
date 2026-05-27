#!/usr/bin/env python
"""
Script d'indexation pour Pinecone (remplace ChromaDB local).
À exécuter UNE SEULE FOIS avant le premier déploiement.

Usage:
  python scripts/ingest_docs_pinecone.py

Prérequis:
  - OPENAI_API_KEY configurée
  - PINECONE_API_KEY configurée
  - PINECONE_INDEX créé sur Pinecone.io
"""

import os
import sys
from pathlib import Path

# Ajouter agent/ au path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

# Charger .env
load_dotenv(Path(__file__).parent.parent / "agent" / ".env")

# Récupérer les clés
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "qa-assistant")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")

# Valider les prérequis
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not set in .env")
if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY not set in .env")

logger.info(f"🔑 Utilisation de l'index Pinecone: {PINECONE_INDEX}")

# ── Initialiser Pinecone ──────────────────────────────────────────────────
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    logger.info(f"✅ Connexion à Pinecone établie")
except Exception as e:
    logger.error(f"❌ Erreur connexion Pinecone: {e}")
    sys.exit(1)

# ── Charger les PDFs ISTQB ────────────────────────────────────────────────
ISTQB_DIR = Path(__file__).parent.parent / "agent" / "rag" / "istqb_docs"

if not ISTQB_DIR.exists():
    logger.warning(f"⚠️  Dossier {ISTQB_DIR} introuvable. Créez-le avec les PDFs ISTQB.")
    sys.exit(1)

pdf_files = list(ISTQB_DIR.glob("*.pdf"))
if not pdf_files:
    logger.error(f"❌ Aucun PDF trouvé dans {ISTQB_DIR}")
    sys.exit(1)

logger.info(f"📄 Trouvé {len(pdf_files)} PDF(s)")

# ── Charger et chunker les documents ──────────────────────────────────────
docs = []
for pdf_path in pdf_files:
    logger.info(f"📖 Chargement {pdf_path.name}...")
    try:
        loader = PyMuPDFLoader(str(pdf_path))
        docs.extend(loader.load())
    except Exception as e:
        logger.error(f"❌ Erreur chargement {pdf_path.name}: {e}")

logger.info(f"✅ {len(docs)} pages chargées")

# Chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=150,
)
chunks = splitter.split_documents(docs)
logger.info(f"✅ {len(chunks)} chunks créés")

# ── Embedding + Indexation ────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)

index = pc.Index(PINECONE_INDEX)
logger.info(f"📤 Indexation dans Pinecone...")

# Batch indexing (par lots de 100)
batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    vectors = []
    
    for j, chunk in enumerate(batch):
        embedding = embeddings.embed_query(chunk.page_content)
        vector_id = f"chunk_{i+j}"
        metadata = {
            "text": chunk.page_content[:512],  # Limiter la taille
            "source": chunk.metadata.get("source", "unknown"),
            "page": chunk.metadata.get("page", 0),
        }
        vectors.append((vector_id, embedding, metadata))
    
    index.upsert(vectors=vectors)
    logger.info(f"  ✓ Batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

logger.info(f"✅ {len(chunks)} chunks indexés avec succès dans Pinecone !")
logger.info(f"🎉 Prêt pour le déploiement Vercel")
