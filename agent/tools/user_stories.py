"""
tools/user_stories.py — Récupération des user stories depuis l'endpoint REST.

Format attendu de l'endpoint (GET) :
[
  {
    "id": 6,
    "index": "US-006",
    "title": "Account creation",
    "description": "As a visitor, I want to...",
    "constraints": ["...", "..."],
    "acceptanceCriteria": ["Given ... When ... Then ..."],
    "priority": "high | medium | low",
    "status": "ready",
    "images": ["generated/us-006-....png"]
  },
  ...
]
"""

import logging
import requests

from config import US_API_ENDPOINT

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5


def fetch_all() -> list[dict]:
    """
    Récupère toutes les user stories depuis l'endpoint configuré.

    Returns:
        Liste de dicts US. Liste vide en cas d'erreur.
    """
    try:
        response = requests.get(US_API_ENDPOINT, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            logger.error("Réponse endpoint inattendue (non-liste) : %s", type(data))
            return []

        logger.info("US récupérées : %d", len(data))
        return data

    except requests.Timeout:
        logger.error("Timeout lors de la récupération des US (%ss)", _TIMEOUT_SECONDS)
        return []
    except requests.HTTPError as e:
        logger.error("Erreur HTTP endpoint US : %s", e)
        return []
    except ValueError as e:
        logger.error("JSON invalide reçu de l'endpoint US : %s", e)
        return []
    except Exception as e:
        logger.error("Erreur inattendue fetch_all : %s", e)
        return []


def fetch_by_index(index: str) -> dict | None:
    """
    Récupère une user story spécifique par son index (ex: "US-006").

    Args:
        index: identifiant de la US, ex: "US-006"

    Returns:
        Dict de la US trouvée, ou None si absente / erreur.
    """
    all_us = fetch_all()
    for us in all_us:
        if us.get("index", "").upper() == index.strip().upper():
            return us

    logger.warning("US non trouvée pour l'index : %s", index)
    return None


def parse_us(us: dict) -> str:
    """
    Formate une user story en texte structuré pour injection dans un prompt LLM.

    Args:
        us: dict d'une user story

    Returns:
        Texte formaté prêt à injecter dans un prompt.
    """
    index = us.get("index", "US-???")
    title = us.get("title", "Sans titre")
    priority = us.get("priority", "unknown")
    description = us.get("description", "")
    constraints = us.get("constraints", [])
    criteria = us.get("acceptanceCriteria", [])

    lines = [
        f"[{index}] {title} (priority: {priority})",
        f"Description: {description}",
    ]

    if constraints:
        lines.append("Constraints:")
        for c in constraints:
            lines.append(f"  - {c}")

    if criteria:
        lines.append("Acceptance Criteria:")
        for ac in criteria:
            lines.append(f"  - {ac}")

    return "\n".join(lines)


def parse_us_list(us_list: list[dict]) -> str:
    """
    Formate une liste de user stories pour injection dans un prompt.

    Args:
        us_list: liste de dicts US

    Returns:
        Texte formaté, chaque US séparée par une ligne vide.
    """
    if not us_list:
        return "Aucune user story disponible."

    return "\n\n".join(parse_us(us) for us in us_list)
