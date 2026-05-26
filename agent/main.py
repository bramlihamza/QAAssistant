"""
main.py — Orchestration principale de l'agent QA (pattern ReAct).

Cycle d'exécution :
  1. Stocker la requête en mémoire courte.
  2. Classifier l'intention.
  3. Rappeler le contexte de conversation.
  4. Si intent QA → récupérer les user stories depuis l'endpoint.
  5. Construire les messages et appeler le LLM (JSON).
  6. Valider la sortie JSON.
  7. Stocker la réponse en mémoire.
  8. Retourner la réponse.
"""

import logging
import os
import re

from llm import call_llm_json
from memory.short_term import store, recall, clear  # noqa: F401 (clear ré-exporté)
from tools.user_stories import fetch_all, fetch_by_index, parse_us_list
from tools.validator import validate_output

logger = logging.getLogger(__name__)

# ── Chargement des prompts ────────────────────────────────────────────────────
_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_prompt(filename: str) -> str:
    path = os.path.join(_PROMPTS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


_SYSTEM_PROMPT = _load_prompt("system.md")
_CLASSIFY_PROMPT = _load_prompt("classify_intent.md")
_GENERATE_PROMPT = _load_prompt("generate_tests.md")

# ── Regex pour détecter un index US dans la requête (ex: US-006) ─────────────
_US_INDEX_PATTERN = re.compile(r"\bUS-\d{3,}\b", re.IGNORECASE)


# ── Fonctions internes ────────────────────────────────────────────────────────

def _classify_intent(query: str) -> dict:
    """
    Identifie l'intention de la requête utilisateur.

    Returns:
        dict avec au moins {"intent": str, "confidence": float, "reason": str}
    """
    messages = [
        {"role": "system", "content": _CLASSIFY_PROMPT},
        {"role": "user",   "content": query},
    ]
    schema = '{"intent":"generate_tests|analyze_story|detect_ambiguities|general|out_of_scope","confidence":0.95,"reason":"..."}'
    try:
        return call_llm_json(messages, schema_hint=schema)
    except RuntimeError as e:
        logger.warning("Échec classification, fallback general : %s", e)
        return {"intent": "general", "confidence": 0.0, "reason": "Fallback après erreur"}


def _build_messages(
    query: str,
    context: list[dict],
    us_list: list[dict],
    intent: str,
) -> list[dict]:
    """
    Construit la liste de messages à envoyer au LLM.

    Args:
        query:   requête utilisateur
        context: historique de conversation (depuis la mémoire courte)
        us_list: liste de user stories récupérées depuis l'endpoint
        intent:  intention classifiée

    Returns:
        Liste de dicts {role, content} prête pour call_llm_json.
    """
    messages = []

    # 1. Prompt système principal
    messages.append({"role": "system", "content": _SYSTEM_PROMPT})

    # 2. Contexte de conversation
    if context:
        ctx_text = "\n".join(
            f"[{m['role'].upper()}] {m['content']}" for m in context
        )
        messages.append({
            "role": "system",
            "content": f"Historique de la conversation :\n{ctx_text}",
        })

    # 3. Données User Stories
    if us_list:
        us_text = parse_us_list(us_list)
        messages.append({
            "role": "system",
            "content": f"User stories disponibles :\n\n{us_text}",
        })
    else:
        messages.append({
            "role": "system",
            "content": "Aucune user story disponible depuis l'endpoint.",
        })

    # 4. Prompt de génération si intent QA
    if intent in ("generate_tests", "analyze_story", "detect_ambiguities"):
        messages.append({"role": "system", "content": _GENERATE_PROMPT})

    # 5. Requête utilisateur
    messages.append({"role": "user", "content": query})

    return messages


def _fetch_relevant_us(query: str, intent: str) -> list[dict]:
    """
    Récupère les user stories pertinentes selon la requête et l'intent.

    - Si un index US est détecté dans la query (ex: US-006), récupère uniquement celle-là.
    - Sinon, récupère toutes les US.
    - Retourne liste vide si intent non QA.
    """
    if intent not in ("generate_tests", "analyze_story", "detect_ambiguities"):
        return []

    # Détecter un index spécifique dans la requête
    match = _US_INDEX_PATTERN.search(query)
    if match:
        index = match.group(0).upper()
        logger.info("Index US détecté dans la requête : %s", index)
        us = fetch_by_index(index)
        return [us] if us else []

    # Sinon, récupérer toutes les US
    return fetch_all()


# ── Fonction principale ───────────────────────────────────────────────────────

def agent(query: str) -> dict:
    """
    Point d'entrée principal de l'agent QA.

    Args:
        query: requête de l'utilisateur (texte libre)

    Returns:
        dict JSON structuré conforme au schéma de l'agent.
    """
    logger.info("Requête reçue : %s", query[:100])

    # 1. Stocker la requête
    store({"role": "user", "content": query})

    # 2. Classifier l'intention
    intent_result = _classify_intent(query)
    intent = intent_result.get("intent", "general")
    logger.info("Intent : %s (confiance : %s)", intent, intent_result.get("confidence"))

    # 3. Rappeler le contexte (hors message courant)
    context = recall(limit=5)[:-1]  # on exclut le message qu'on vient de stocker

    # 4. Récupérer les user stories pertinentes
    us_list = _fetch_relevant_us(query, intent)
    logger.info("US chargées : %d", len(us_list))

    # 5. Construire les messages et appeler le LLM
    messages = _build_messages(query, context, us_list, intent)

    schema = (
        '{"status":"success|error|clarification_needed|out_of_scope",'
        '"intent":"generate_tests|analyze_story|detect_ambiguities|general|out_of_scope",'
        '"answer":"...","test_cases":[],"ambiguities":[],'
        '"sources":[],"warnings":[],"requires_human_validation":true}'
    )

    try:
        response = call_llm_json(messages, schema_hint=schema)
    except RuntimeError as e:
        logger.error("Erreur LLM : %s", e)
        error_response = {
            "status": "error",
            "intent": intent,
            "answer": "Une erreur est survenue lors de la génération. Veuillez réessayer.",
            "test_cases": [],
            "ambiguities": [],
            "sources": [],
            "warnings": [str(e)],
            "requires_human_validation": True,
        }
        store({"role": "assistant", "content": error_response["answer"]})
        return error_response

    # 6. Valider la sortie
    try:
        validate_output(response)
    except ValueError as e:
        logger.warning("Validation sortie échouée : %s", e)
        response["warnings"] = response.get("warnings", []) + [f"Validation: {e}"]

    # 7. Stocker la réponse
    store({"role": "assistant", "content": response.get("answer", "")})

    logger.info(
        "Réponse générée — status=%s, test_cases=%d",
        response.get("status"),
        len(response.get("test_cases", [])),
    )

    return response
