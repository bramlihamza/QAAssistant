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
import re
import requests

from config import US_API_ENDPOINT

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5
_US_INDEX_PATTERN = re.compile(r"^US-(\d+)$", re.IGNORECASE)

_GITHUB_DEFAULT_DATA_BASE = (
    "https://raw.githubusercontent.com/"
    "mickaellherminez/github-user-stories-fake-api/main/data"
)
_GITHUB_DEFAULT_LIST_URL = f"{_GITHUB_DEFAULT_DATA_BASE}/user-stories.json"


def _resolve_user_stories_url(endpoint: str) -> str:
    """
    Accepte soit :
      - une URL directe vers user-stories.json
      - une base URL terminant par /data
    """
    normalized = endpoint.strip().rstrip("/")
    if normalized.endswith("user-stories.json"):
        return normalized
    if normalized.endswith("/data"):
        return f"{normalized}/user-stories.json"
    return normalized


def _resolve_user_story_by_id_url(endpoint: str, story_id: int) -> str | None:
    """
    Construit l'URL d'une US individuelle à partir d'un endpoint.

    Exemples supportés :
      - .../data                  -> .../data/user-stories/{id}.json
      - .../data/user-stories.json -> .../data/user-stories/{id}.json
    """
    normalized = endpoint.strip().rstrip("/")
    if normalized.endswith("/data"):
        return f"{normalized}/user-stories/{story_id}.json"
    if normalized.endswith("user-stories.json"):
        base = normalized.rsplit("/", 1)[0]
        return f"{base}/user-stories/{story_id}.json"
    return None


def _fetch_json(url: str) -> object | None:
    try:
        response = requests.get(url, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        logger.error("Timeout lors de la récupération des US (%ss) : %s", _TIMEOUT_SECONDS, url)
        return None
    except requests.HTTPError as e:
        logger.error("Erreur HTTP endpoint US (%s) : %s", url, e)
        return None
    except ValueError as e:
        logger.error("JSON invalide reçu de l'endpoint US (%s) : %s", url, e)
        return None
    except Exception as e:
        logger.error("Erreur inattendue fetch US (%s) : %s", url, e)
        return None


def fetch_all() -> list[dict]:
    """
    Récupère toutes les user stories depuis l'endpoint configuré.

    Returns:
        Liste de dicts US. Liste vide en cas d'erreur.
    """
    candidate_urls = [_resolve_user_stories_url(US_API_ENDPOINT)]
    if _GITHUB_DEFAULT_LIST_URL not in candidate_urls:
        candidate_urls.append(_GITHUB_DEFAULT_LIST_URL)

    for url in candidate_urls:
        payload = _fetch_json(url)
        if not isinstance(payload, list):
            logger.warning("Réponse US inattendue (non-liste) depuis %s : %s", url, type(payload))
            continue

        data = [item for item in payload if isinstance(item, dict)]
        if data:
            logger.info("US récupérées : %d (source=%s)", len(data), url)
            return data

        logger.warning("Liste US vide depuis %s", url)

    return []


def fetch_by_index(index: str) -> dict | None:
    """
    Récupère une user story spécifique par son index (ex: "US-006").

    Args:
        index: identifiant de la US, ex: "US-006"

    Returns:
        Dict de la US trouvée, ou None si absente / erreur.
    """
    normalized_index = index.strip().upper()

    all_us = fetch_all()
    for us in all_us:
        if us.get("index", "").upper() == normalized_index:
            return us

    # Fallback par ID pour les endpoints qui exposent /user-stories/{id}.json
    match = _US_INDEX_PATTERN.match(normalized_index)
    if not match:
        logger.warning("US non trouvée pour l'index : %s", normalized_index)
        return None

    story_id = int(match.group(1))
    candidate_urls: list[str] = []
    per_id_url = _resolve_user_story_by_id_url(US_API_ENDPOINT, story_id)
    if per_id_url:
        candidate_urls.append(per_id_url)
    default_per_id_url = f"{_GITHUB_DEFAULT_DATA_BASE}/user-stories/{story_id}.json"
    if default_per_id_url not in candidate_urls:
        candidate_urls.append(default_per_id_url)

    for url in candidate_urls:
        payload = _fetch_json(url)
        if isinstance(payload, dict):
            payload_index = str(payload.get("index", "")).upper()
            if payload_index == normalized_index:
                logger.info("US %s récupérée via fallback (%s)", normalized_index, url)
                return payload

    logger.warning("US non trouvée pour l'index : %s", normalized_index)
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
