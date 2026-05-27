"""
Endpoint Vercel : GET /api/user-stories
Retourne la liste des user stories disponibles.
"""

import json
import os
import sys
from pathlib import Path
from api.utils import success_response, error_response, cors_headers

# Import du code existant
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))


def handler(request):
    """Handler Vercel pour GET /api/user-stories"""
    
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
    
    try:
        from tools.user_stories import fetch_all
        
        # Récupère toutes les user stories
        us_list = fetch_all()
        
        response = success_response({
            "status": "success",
            "count": len(us_list),
            "user_stories": us_list
        })
        response["headers"].update(cors_headers())
        return response
    
    except Exception as e:
        response = error_response(f"Erreur lecture user stories: {str(e)}", 500)
        response["headers"].update(cors_headers())
        return response
