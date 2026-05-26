"""
security/output_filter.py — Filtrage des données sensibles dans les sorties de l'agent.

Masque automatiquement les patterns suivants dans les champs texte :
  - Adresses email          → [EMAIL]
  - Numéros de téléphone    → [TELEPHONE]
  - Numéros de carte bancaire → [CARTE]
  - Numéros de sécurité sociale (FR) → [NIR]

Usage :
    from security.output_filter import filter_response
    safe_response = filter_response(response_dict)
"""

import re
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)

# ── Patterns de données sensibles ─────────────────────────────────────────────
_SENSITIVE_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Email
    (re.compile(r"[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}", re.IGNORECASE), "[EMAIL]"),
    # Téléphone FR : 06 12 34 56 78 / +33612345678 / 0612345678
    (re.compile(r"(\+33|0033|0)[1-9](\s?\d{2}){4}"), "[TELEPHONE]"),
    # Carte bancaire : 16 chiffres groupés ou non
    (re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"), "[CARTE]"),
    # NIR / numéro de sécu FR : 13 chiffres + clé 2 chiffres
    (re.compile(r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b"), "[NIR]"),
]

# Champs texte de la réponse à filtrer
_TEXT_FIELDS = ("answer", "warnings")


def _mask_text(text: str) -> tuple[str, int]:
    """
    Applique tous les patterns de masquage sur un texte.

    Returns:
        (texte_masqué, nombre_de_remplacements)
    """
    total = 0
    for pattern, mask in _SENSITIVE_PATTERNS:
        text, count = pattern.subn(mask, text)
        total += count
    return text, total


def filter_response(response: dict) -> dict:
    """
    Filtre les données sensibles dans la réponse de l'agent.

    Travaille sur une copie profonde — la réponse originale n'est pas modifiée.

    Args:
        response: dict retourné par l'agent.

    Returns:
        Copie du dict avec les données sensibles masquées.
    """
    if not isinstance(response, dict):
        return response

    filtered = deepcopy(response)
    total_replacements = 0

    # Filtrage des champs texte de premier niveau
    for field in _TEXT_FIELDS:
        value = filtered.get(field)
        if isinstance(value, str):
            filtered[field], count = _mask_text(value)
            total_replacements += count
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, str):
                    masked, count = _mask_text(item)
                    new_list.append(masked)
                    total_replacements += count
                else:
                    new_list.append(item)
            filtered[field] = new_list

    # Filtrage dans les cas de test (données_fictives peuvent contenir des emails)
    for tc in filtered.get("test_cases", []):
        if isinstance(tc, dict):
            # Champ données_fictives (dict)
            df = tc.get("données_fictives", {})
            if isinstance(df, dict):
                for key, val in df.items():
                    if isinstance(val, str):
                        df[key], count = _mask_text(val)
                        total_replacements += count
            # Champ résultat_attendu
            if isinstance(tc.get("résultat_attendu"), str):
                tc["résultat_attendu"], count = _mask_text(tc["résultat_attendu"])
                total_replacements += count

    if total_replacements > 0:
        logger.warning(
            "Données sensibles masquées dans la réponse : %d remplacement(s).",
            total_replacements,
        )

    return filtered
