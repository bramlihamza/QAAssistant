"""
tools/validator.py — Validation du JSON de sortie de l'agent.

Vérifie que la réponse produite par le LLM respecte le schéma attendu
avant de la retourner à l'appelant.
"""

import logging

logger = logging.getLogger(__name__)

# Champs obligatoires dans toute réponse de l'agent
_REQUIRED_TOP_LEVEL = {"status", "intent", "answer"}

# Champs obligatoires dans chaque cas de test
_REQUIRED_TEST_CASE = {"id", "titre", "catégorie", "résultat_attendu", "user_story"}

# Valeurs valides
_VALID_STATUSES = {"success", "error", "clarification_needed", "out_of_scope"}
_VALID_INTENTS = {"generate_tests", "analyze_story", "detect_ambiguities", "general", "out_of_scope"}
_VALID_CATEGORIES = {"positive", "negative", "limite"}


def validate_output(response: dict) -> None:
    """
    Valide la structure de la réponse JSON de l'agent.

    Args:
        response: dict retourné par call_llm_json

    Raises:
        ValueError: si un champ obligatoire est absent ou invalide.
    """
    if not isinstance(response, dict):
        raise ValueError(f"La réponse doit être un dict, reçu : {type(response)}")

    # Champs de premier niveau
    missing = _REQUIRED_TOP_LEVEL - response.keys()
    if missing:
        raise ValueError(f"Champs manquants dans la réponse : {missing}")

    # Statut valide
    status = response.get("status")
    if status not in _VALID_STATUSES:
        logger.warning("Statut inattendu : '%s' (accepté mais non standard)", status)

    # Intent valide
    intent = response.get("intent")
    if intent not in _VALID_INTENTS:
        logger.warning("Intent inattendu : '%s' (accepté mais non standard)", intent)

    # Validation des cas de test si intent = generate_tests
    if intent == "generate_tests":
        test_cases = response.get("test_cases")
        if not isinstance(test_cases, list):
            raise ValueError(
                "Le champ 'test_cases' doit être une liste "
                f"(reçu : {type(test_cases)})."
            )

        for i, tc in enumerate(test_cases):
            _validate_test_case(tc, index=i)

    logger.debug("Validation sortie OK — status=%s, intent=%s", status, intent)


def _validate_test_case(tc: dict, index: int) -> None:
    """
    Valide un cas de test individuel.

    Args:
        tc:    dict du cas de test
        index: position dans la liste (pour les messages d'erreur)
    """
    if not isinstance(tc, dict):
        raise ValueError(f"test_cases[{index}] doit être un dict (reçu : {type(tc)})")

    missing = _REQUIRED_TEST_CASE - tc.keys()
    if missing:
        raise ValueError(
            f"test_cases[{index}] — champs manquants : {missing} "
            f"(id={tc.get('id', '?')})"
        )

    categorie = tc.get("catégorie", "")
    if categorie not in _VALID_CATEGORIES:
        logger.warning(
            "test_cases[%d] catégorie inattendue : '%s' (attendu : %s)",
            index, categorie, _VALID_CATEGORIES,
        )
