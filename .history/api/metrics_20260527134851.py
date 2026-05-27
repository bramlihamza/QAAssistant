"""
Endpoint Vercel : GET /api/metrics
Retourne les statistiques d'utilisation.

Note: En serverless, les métriques sont stockées par requête.
Pour une persistance, utilisez une base de données externe.
"""

import json
import os
from datetime import datetime
from api.utils import success_response, cors_headers


def handler(request):
    """Handler Vercel pour GET /api/metrics"""
    
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "body": "",
            "headers": cors_headers()
        }
    
    if request.method != "GET":
        return {
            "statusCode": 405,
            "body": json.dumps({"status": "error", "message": "Utilisez GET"}),
            "headers": cors_headers()
        }
    
    # Métriques (non persistantes en serverless)
    # Pour la persistance, intégrez une DB (Supabase, MongoDB, etc.)
    metrics = {
        "note": "Métriques en temps réel par container (non persistantes)",
        "info": "Pour persistance, utilisez une base de données externe",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": {
            "openai_model": os.getenv("MODEL", "gpt-4o-mini"),
            "temperature": float(os.getenv("TEMPERATURE", "0")),
            "platform": "vercel",
            "runtime": "python"
        }
    }
    
    response = success_response(metrics)
    response["headers"].update(cors_headers())
    return response
