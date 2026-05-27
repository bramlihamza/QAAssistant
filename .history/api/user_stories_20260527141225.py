"""
Endpoint Vercel : GET /api/user-stories
Retourne la liste des user stories disponibles.
"""

import json
import os
from datetime import datetime


def handler(request):
    """Handler Vercel pour GET /api/user-stories"""
    
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
    
    try:
        # TODO: Intégrer la lecture depuis le fichier user_stories_45_generated.json
        # Pour maintenant, retournez un stub
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "count": 0,
                "message": "User stories endpoint en cours de configuration",
                "user_stories": [],
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
                "message": f"Erreur lecture user stories: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }
        }
