"""Tests unitaires — tools/user_stories.py + tools/validator.py"""

import pytest
from unittest.mock import patch, Mock

from tools.user_stories import fetch_all, fetch_by_index, parse_us, parse_us_list
from tools.validator import validate_output


# ── Fixtures ──────────────────────────────────────────────────────────────────

US_006 = {
    "id": 6,
    "index": "US-006",
    "title": "Account creation",
    "description": "As a visitor, I want to create an account so that I can start using the platform.",
    "constraints": [
        "The email address must be unique.",
        "The password must contain at least 8 characters.",
    ],
    "acceptanceCriteria": [
        "Given a valid registration form, when the user submits it, then the account is created.",
        "Given an email already in use, when the user submits the form, then an error message is displayed.",
    ],
    "priority": "high",
    "status": "ready",
    "images": ["generated/us-006-account-creation.png"],
}

US_007 = {
    "id": 7,
    "index": "US-007",
    "title": "Email verification",
    "description": "As a new user, I want to verify my email.",
    "constraints": ["The verification link must be unique."],
    "acceptanceCriteria": ["Given a valid link, when clicked, then the account is activated."],
    "priority": "high",
    "status": "ready",
    "images": [],
}

VALID_RESPONSE = {
    "status": "success",
    "intent": "generate_tests",
    "answer": "12 cas de test générés pour US-006.",
    "test_cases": [
        {
            "id": "TC-001",
            "titre": "Création de compte avec données valides",
            "catégorie": "positive",
            "préconditions": "L'utilisateur n'est pas connecté.",
            "étapes": ["Remplir le formulaire", "Soumettre"],
            "données_fictives": {"email": "test@example.com", "password": "Password1!"},
            "résultat_attendu": "Le compte est créé.",
            "priorité": "high",
            "user_story": "US-006",
            "status": "à valider",
        }
    ],
    "ambiguities": [],
    "sources": ["US-006"],
    "warnings": [],
    "requires_human_validation": True,
}


# ── fetch_all ─────────────────────────────────────────────────────────────────

def test_fetch_all_success():
    mock_resp = Mock()
    mock_resp.json.return_value = [US_006, US_007]
    mock_resp.raise_for_status = Mock()

    with patch("tools.user_stories.requests.get", return_value=mock_resp):
        result = fetch_all()

    assert len(result) == 2
    assert result[0]["index"] == "US-006"


def test_fetch_all_timeout():
    import requests as req
    with patch("tools.user_stories.requests.get", side_effect=req.Timeout):
        result = fetch_all()
    assert result == []


def test_fetch_all_http_error():
    import requests as req
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = req.HTTPError("404")
    with patch("tools.user_stories.requests.get", return_value=mock_resp):
        result = fetch_all()
    assert result == []


def test_fetch_all_non_list_response():
    mock_resp = Mock()
    mock_resp.json.return_value = {"error": "not a list"}
    mock_resp.raise_for_status = Mock()
    with patch("tools.user_stories.requests.get", return_value=mock_resp):
        result = fetch_all()
    assert result == []


# ── fetch_by_index ────────────────────────────────────────────────────────────

def test_fetch_by_index_found():
    mock_resp = Mock()
    mock_resp.json.return_value = [US_006, US_007]
    mock_resp.raise_for_status = Mock()

    with patch("tools.user_stories.requests.get", return_value=mock_resp):
        result = fetch_by_index("US-006")

    assert result is not None
    assert result["title"] == "Account creation"


def test_fetch_by_index_case_insensitive():
    mock_resp = Mock()
    mock_resp.json.return_value = [US_006]
    mock_resp.raise_for_status = Mock()

    with patch("tools.user_stories.requests.get", return_value=mock_resp):
        result = fetch_by_index("us-006")

    assert result is not None


def test_fetch_by_index_not_found():
    mock_resp = Mock()
    mock_resp.json.return_value = [US_006]
    mock_resp.raise_for_status = Mock()

    with patch("tools.user_stories.requests.get", return_value=mock_resp):
        result = fetch_by_index("US-999")

    assert result is None


# ── parse_us ──────────────────────────────────────────────────────────────────

def test_parse_us_contains_key_fields():
    text = parse_us(US_006)
    assert "US-006" in text
    assert "Account creation" in text
    assert "high" in text
    assert "The email address must be unique." in text
    assert "Given a valid registration form" in text


def test_parse_us_empty_us():
    text = parse_us({})
    assert "US-???" in text


def test_parse_us_list_multiple():
    text = parse_us_list([US_006, US_007])
    assert "US-006" in text
    assert "US-007" in text


def test_parse_us_list_empty():
    text = parse_us_list([])
    assert "Aucune" in text


# ── validate_output ───────────────────────────────────────────────────────────

def test_validate_output_valid():
    validate_output(VALID_RESPONSE)  # Ne doit pas lever d'exception


def test_validate_output_missing_status():
    bad = {**VALID_RESPONSE}
    del bad["status"]
    with pytest.raises(ValueError, match="status"):
        validate_output(bad)


def test_validate_output_missing_answer():
    bad = {**VALID_RESPONSE}
    del bad["answer"]
    with pytest.raises(ValueError, match="answer"):
        validate_output(bad)


def test_validate_output_test_cases_not_list():
    bad = {**VALID_RESPONSE, "test_cases": "pas une liste"}
    with pytest.raises(ValueError, match="test_cases"):
        validate_output(bad)


def test_validate_output_test_case_missing_field():
    bad_tc = {k: v for k, v in VALID_RESPONSE["test_cases"][0].items() if k != "user_story"}
    bad = {**VALID_RESPONSE, "test_cases": [bad_tc]}
    with pytest.raises(ValueError, match="user_story"):
        validate_output(bad)


def test_validate_output_non_dict():
    with pytest.raises(ValueError, match="dict"):
        validate_output("pas un dict")
