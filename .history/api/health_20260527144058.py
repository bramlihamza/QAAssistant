"""
Endpoint Vercel : GET /api/health
Vérifie l'état de l'API.
"""

import json
import os
from datetime import datetime


def handler(request):
    """Handler Vercel pour GET /api/health"""
    
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }
    
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                **headers,
                "Access-Control-Allow-Methods": "GET, OPTIONS",
            }
        }
    
    if request.method != "GET":
        return {
            "statusCode": 405,
            "body": json.dumps({"status": "error", "message": "Utilisez GET"}),
            "headers": headers
        }
    
    # Vérifications
    checks = {
        "api": "✅ OK",
        "openai_api_key": "✅ Configured" if os.getenv("OPENAI_API_KEY") else "❌ Missing",
        "pinecone_api_key": "✅ Configured" if os.getenv("PINECONE_API_KEY") else "❌ Missing",
        "pinecone_index": "✅ Configured" if os.getenv("PINECONE_INDEX") else "❌ Missing",
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
        "headers": headers
    }
