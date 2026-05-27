"""
Endpoint Vercel : POST /api/ask
Soumet une question à l'agent QA.
"""

import json
import os
import sys
import logging
from pathlib import Path

# Import du code existant du projet
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))

from api.utils import error_response, success_response, cors_headers, OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX

logger = logging.getLogger(__name__)

# Cache en mémoire (vivra pendant la durée de l'exécution serverless)
_agent_cache = None
_last_init_time = None


def _initialize_agent():
    """Initialise l'agent QA une fois (réutilisé dans le même container)."""
    global _agent_cache, _last_init_time
    
    if _agent_cache is not None:
        return _agent_cache
    
    try:
        # Import lazy pour éviter les dépendances lourdes
        from main import agent
        _agent_cache = agent
        _last_init_time = os.times()
        logger.info("✅ Agent QA initialisé")
        return _agent_cache
    except Exception as e:
        logger.error(f"❌ Erreur init agent: {str(e)}")
        raise


def handler(request):
    """Handler Vercel pour POST /api/ask"""
    
    # Gestion OPTIONS (CORS preflight)
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "body": "",
            "headers": cors_headers()
        }
    
    if request.method != "POST":
        response = error_response("Méthode non autorisée. Utilisez POST.", 405)
        response["headers"].update(cors_headers())
        return response
    
    try:
        # Parse JSON body
        body = json.loads(request.body) if isinstance(request.body, str) else request.body
        question = body.get("question", "").strip()
        
        if not question:
            response = error_response("'question' est obligatoire.")
            response["headers"].update(cors_headers())
            return response
        
        # Récupère l'agent
        agent = _initialize_agent()
        
        # Exécute l'agent
        result = agent(question)
        
        # Retourne le résultat
        response = success_response({
            "status": "success",
            "question": question,
            "answer": result.get("answer", ""),
            "test_cases": result.get("test_cases", []),
            "warnings": result.get("warnings", []),
            "sources": result.get("sources", []),
            "requires_human_validation": True
        })
        response["headers"].update(cors_headers())
        return response
    
    except json.JSONDecodeError:
        response = error_response("JSON invalide dans le body.")
        response["headers"].update(cors_headers())
        return response
    
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}", exc_info=True)
        response = error_response(f"Erreur serveur: {str(e)}", 500)
        response["headers"].update(cors_headers())
        return response
