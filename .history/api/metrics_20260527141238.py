"""
Endpoint Vercel : GET /api/metrics
Retourne les statistiques d'utilisation.

Note: En serverless, les métriques sont stockées par requête.
Pour une persistance, utilisez une base de données externe.
"""

import json
import os
from datetime import datetime


def handler(request):
    """Handler Vercel pour GET /api/metrics"""
    
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
    
    # Métriques (non persistantes en serverless)
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
    
    return {
        "statusCode": 200,
        "body": json.dumps(metrics),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }
    }
