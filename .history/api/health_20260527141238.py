"""
Endpoint Vercel : GET /api/health
Vérifie l'état de santé de l'API et de ses dépendances.
"""

import json
import os
from datetime import datetime


def handler(request):
    """Handler Vercel pour GET /api/health"""
    
    # Gestion OPTIONS
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
    
    if request.method != "GET":
        return {
            "statusCode": 405,
            "body": json.dumps({"status": "error", "message": "Utilisez GET"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        }
    
    # Vérifications
    checks = {
        "api": "✅ OK",
        "openai_api_key": "✅ Configuré" if os.getenv("OPENAI_API_KEY") else "❌ Manquant",
        "pinecone_api_key": "✅ Configuré" if os.getenv("PINECONE_API_KEY") else "❌ Manquant",
        "pinecone_index": "✅ Configuré" if os.getenv("PINECONE_INDEX") else "❌ Manquant",
    }
    
    all_ok = all("✅" in v for v in checks.values())
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "healthy" if all_ok else "degraded",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0"
        }),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }
    }
