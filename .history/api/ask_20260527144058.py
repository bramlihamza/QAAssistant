"""
Endpoint Vercel : POST /api/ask
Génère des cas de test via l'agent QA.
"""

import json
import os
from datetime import datetime


def handler(request):
    """Handler Vercel pour POST /api/ask"""
    
    # CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        }
    
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }
    
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({
                "status": "error",
                "message": "Méthode non autorisée. Utilisez POST.",
            }),
            "headers": headers
        }
    
    try:
        # Parse body
        if isinstance(request.body, bytes):
            body = json.loads(request.body.decode())
        else:
            body = json.loads(request.body) if isinstance(request.body, str) else request.body
        
        question = body.get("question", "").strip()
        
        if not question:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "'question' est obligatoire.",
                }),
                "headers": headers
            }
        
        # Vérifier configuration
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "❌ OPENAI_API_KEY not configured in Vercel",
                }),
                "headers": headers
            }
        
        if not os.getenv("PINECONE_API_KEY"):
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "❌ PINECONE_API_KEY not configured in Vercel",
                }),
                "headers": headers
            }
        
        # Stub response (agent à intégrer)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "question": question,
                "answer": "Endpoint /api/ask opérationnel sur Vercel.",
                "test_cases": [],
                "warnings": ["⚠️  Agent QA en cours d'intégration"],
                "sources": [],
                "requires_human_validation": True,
                "timestamp": datetime.utcnow().isoformat()
            }),
            "headers": headers
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": f"Erreur: {str(e)}",
            }),
            "headers": headers
        }
