"""
Adaptateur Vercel pour QA Assistant.
Interfaces entre Vercel Functions et le code existant.
"""

import os
import json
from typing import Any, Dict
from datetime import datetime

# Variables d'env requises pour Vercel
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "qa-assistant")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not set")
if not PINECONE_API_KEY:
    raise ValueError("❌ PINECONE_API_KEY not set")


def error_response(message: str, status_code: int = 400):
    """Retourne une réponse d'erreur standardisée."""
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "status": "error",
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }),
        "headers": {"Content-Type": "application/json"}
    }


def success_response(data: Dict[str, Any], status_code: int = 200):
    """Retourne une réponse de succès standardisée."""
    return {
        "statusCode": status_code,
        "body": json.dumps(data),
        "headers": {"Content-Type": "application/json"}
    }


def cors_headers():
    """Headers CORS pour Vercel."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
