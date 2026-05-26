"""
security/input_guard.py — Validation et assainissement des inputs utilisateur.

Deux protections :
  1. Longueur maximale (5000 caractères).
  2. Détection de patterns de prompt injection.

Usage :
    ok, result = validate_input(question)
    if not ok:
        return {"status": "error", "answer": result}
    clean_question = result
"""

import re
import logging

logger = logging.getLogger(__name__)

MAX_INPUT_LENGTH = 5000

# ── Patterns de prompt injection ──────────────────────────────────────────────
# Chaque pattern est une regex case-insensitive détectant une tentative
# de manipulation du prompt système.
_INJECTION_PATTERNS: list[tuple[str, str]] = [
    # Tentatives de réinitialisation du rôle
    (r"ignore\s+.{0,30}(instructions?|rules?|prompt)", "reset role"),
    (r"(oublie|forget|disregard)\s+.{0,30}(instructions?|consignes?|rules?)", "reset role"),
    (r"tu\s+es\s+maintenant", "role reassignment"),
    (r"you\s+are\s+now\s+a", "role reassignment"),
    (r"act\s+as\s+(if\s+you\s+are|a\s+different)", "role reassignment"),
    # Exfiltration du prompt système
    (r"(répète|repeat|show|display|reveal|affiche)\s+.{0,30}(system\s*prompt|instructions?|consignes?)", "prompt exfiltration"),
    (r"what\s+(are|were)\s+your\s+(instructions?|rules?|system\s*prompt)", "prompt exfiltration"),
    (r"(montre|affiche)\s+.{0,30}(prompt|instructions?|système)", "prompt exfiltration"),
    # Injection de rôle via balises
    (r"<\s*system\s*>", "tag injection"),
    (r"\[INST\]", "tag injection"),
    (r"###\s*(system|instruction|prompt)", "tag injection"),
    # Tentatives de jailbreak classiques
    (r"(DAN|jailbreak|do\s+anything\s+now)", "jailbreak"),
    (r"pretend\s+(you\s+are|that\s+you)", "jailbreak"),
    (r"(simulate|roleplay)\s+(being|as)\s+", "jailbreak"),
]

_COMPILED_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE | re.DOTALL), label)
    for pattern, label in _INJECTION_PATTERNS
]


def validate_input(question: str) -> tuple[bool, str]:
    """
    Valide et nettoie la requête utilisateur.

    Args:
        question: texte brut soumis par l'utilisateur.

    Returns:
        (True, question_nettoyée) si valide.
        (False, message_erreur) si invalide ou suspecte.
    """
    # 1. Vérification nullité
    if not question or not question.strip():
        logger.warning("Input vide reçu.")
        return False, "La question ne peut pas être vide."

    question = question.strip()

    # 2. Troncature silencieuse si dépassement
    if len(question) > MAX_INPUT_LENGTH:
        logger.warning(
            "Input tronqué : %d → %d caractères.", len(question), MAX_INPUT_LENGTH
        )
        question = question[:MAX_INPUT_LENGTH]

    # 3. Détection de prompt injection
    for pattern, label in _COMPILED_PATTERNS:
        if pattern.search(question):
            logger.warning("Prompt injection détectée [%s] : %.80s", label, question)
            return False, (
                "Cette requête n'est pas autorisée. "
                "Veuillez soumettre une user story ou une question QA valide."
            )

    return True, question
