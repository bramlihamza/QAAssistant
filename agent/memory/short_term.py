"""
memory/short_term.py — Mémoire de session (court terme).

Stocke l'historique de la conversation courante en mémoire Python.
Chaque message est un dict {role, content} avec role ∈ {user, assistant, system, tool}.

Limites :
- MAX_MEMORY = 10 messages maximum conservés.
- La mémoire est réinitialisée à chaque redémarrage du processus.
- Pour une persistance inter-sessions, utiliser la mémoire longue (long_term.py).
"""

import logging

logger = logging.getLogger(__name__)

MAX_MEMORY: int = 10

_memory: list[dict] = []


def store(message: dict) -> None:
    """
    Ajoute un message en mémoire et tronque si nécessaire.

    Args:
        message: dict avec au minimum {"role": str, "content": str}
    """
    if not isinstance(message, dict) or "role" not in message or "content" not in message:
        logger.warning("Message ignoré (format invalide) : %s", message)
        return

    _memory.append(message)

    if len(_memory) > MAX_MEMORY:
        removed = len(_memory) - MAX_MEMORY
        del _memory[:removed]
        logger.debug("Mémoire tronquée : %d message(s) supprimé(s)", removed)


def recall(limit: int = 5) -> list[dict]:
    """
    Retourne les N derniers messages de la mémoire.

    Args:
        limit: nombre maximum de messages à retourner (défaut : 5)

    Returns:
        Liste des messages les plus récents, du plus ancien au plus récent.
    """
    return _memory[-limit:] if limit > 0 else []


def clear() -> None:
    """Vide entièrement la mémoire de session."""
    _memory.clear()
    logger.debug("Mémoire effacée.")


def size() -> int:
    """Retourne le nombre de messages actuellement en mémoire."""
    return len(_memory)
