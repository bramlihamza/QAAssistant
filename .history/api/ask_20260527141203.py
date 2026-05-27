"""
Endpoint Vercel : POST /api/ask
Soumet une question à l'agent QA.
"""

import json
import os
from datetime import datetime


def handler(request):
    """Handler Vercel pour POST /api/ask"""
    
    # Gestion OPTIONS (CORS preflight)
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "body": "",
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        }
    
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({
                "status": "error",
                "message": "Méthode non autorisée. Utilisez POST.",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        }
    
    try:
        # Parse JSON body
        if isinstance(request.body, str):
            body = json.loads(request.body)
        else:
            body = request.body
        
        question = body.get("question", "").strip()
        
        if not question:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "status": "error",
                    "message": "'question' est obligatoire.",
                    "timestamp": datetime.utcnow().isoformat()
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                }
            }
        
        # Vérifier les clés API
        if not os.getenv("OPENAI_API_KEY"):
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "OPENAI_API_KEY not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                }
            }
        
        if not os.getenv("PINECONE_API_KEY"):
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "PINECONE_API_KEY not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                }
            }
        
        # Retourne un stub de réponse pour maintenant
        # TODO: Intégrer l'agent QA complet
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "question": question,
                "answer": "Endpoint /api/ask est opérationnel. Agent en cours d'intégration.",
                "test_cases": [],
                "warnings": ["⚠️  Agent QA en cours de configuration"],
                "sources": [],
                "requires_human_validation": True,
                "timestamp": datetime.utcnow().isoformat()
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        }
    
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "status": "error",
                "message": "JSON invalide dans le body.",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": f"Erreur serveur: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        }
