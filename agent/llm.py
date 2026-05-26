"""
llm.py — Abstraction LLM via LangChain (ChatOpenAI).

Deux fonctions publiques :
  - call_llm(messages)          → str
  - call_llm_json(messages)     → dict

Le modèle, la température et les autres paramètres
sont lus depuis config.py — ne pas les passer en dur ici.
"""

import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from config import OPENAI_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

logger = logging.getLogger(__name__)

# ── Instance partagée ─────────────────────────────────────────────────────────
_llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=MODEL,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)


def _build_lc_messages(messages: list[dict]) -> list:
    """
    Convertit une liste de dicts {role, content} en objets LangChain.

    Rôles supportés : "system", "user", "assistant".
    """
    lc_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))
    return lc_messages


def call_llm(messages: list[dict]) -> str:
    """
    Appelle le LLM et retourne la réponse brute en texte.

    Args:
        messages: liste de dicts {"role": "system|user|assistant", "content": "..."}

    Returns:
        Contenu texte de la réponse.

    Raises:
        RuntimeError: en cas d'erreur API.
    """
    try:
        lc_msgs = _build_lc_messages(messages)
        response = _llm.invoke(lc_msgs)
        content = response.content
        logger.debug("LLM response (truncated): %s", content[:200])
        return content
    except Exception as e:
        logger.error("Erreur appel LLM : %s", e)
        raise RuntimeError(f"Erreur appel LLM : {e}") from e


def call_llm_json(messages: list[dict], schema_hint: str = "") -> dict:
    """
    Appelle le LLM en forçant une sortie JSON valide.

    Un message système supplémentaire est injecté pour instruire
    le modèle de répondre uniquement en JSON selon schema_hint.

    Args:
        messages:    liste de dicts {role, content}.
        schema_hint: exemple de schéma JSON attendu (string).

    Returns:
        dict parsé depuis la réponse JSON.

    Raises:
        RuntimeError: si la réponse n'est pas du JSON valide.
    """
    json_instruction = (
        "Tu dois répondre UNIQUEMENT en JSON valide, sans texte avant ni après. "
        "N'utilise pas de blocs markdown (```json). "
    )
    if schema_hint:
        json_instruction += f"Schéma attendu : {schema_hint}"

    augmented = [{"role": "system", "content": json_instruction}] + messages

    raw = call_llm(augmented)

    # Nettoyage défensif : retirer d'éventuels blocs markdown
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("JSON invalide reçu du LLM : %s\nRéponse brute : %s", e, raw)
        raise RuntimeError(f"Réponse LLM non JSON : {e}\nRéponse brute : {raw}") from e
