"""
config.py — Chargement centralisé de la configuration.

Toutes les variables d'environnement sont lues ici.
Aucun autre module ne doit appeler os.getenv directement.
"""

import os
from dotenv import load_dotenv

# Chargement du fichier .env situé dans le même répertoire
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def _require(key: str) -> str:
    """Lève une erreur explicite si une variable obligatoire est absente."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Variable d'environnement manquante : '{key}'. "
            f"Vérifiez votre fichier .env (voir .env.example)."
        )
    return value


# ── LLM ──────────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = _require("OPENAI_API_KEY")
MODEL: str = os.getenv("MODEL", "gpt-4o-mini")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

# ── RAG / ChromaDB ────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
RAG_SCORE_THRESHOLD: float = float(os.getenv("RAG_SCORE_THRESHOLD", "0.70"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
