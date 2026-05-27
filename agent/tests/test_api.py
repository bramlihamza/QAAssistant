"""
Tests de l'API FastAPI — sans appels réseau réels ni LLM.

Utilise httpx.AsyncClient + mock de agent() et is_indexed().
"""

import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport

# Réponse-type renvoyée par l'agent mocké
_AGENT_SUCCESS = {
    "status": "success",
    "intent": "generate_tests",
    "answer": "J'ai généré 2 cas de test pour US-006.",
    "test_cases": [
        {
            "id": "TC-001",
            "titre": "Création de compte avec email valide",
            "catégorie": "positive",
            "préconditions": "L'utilisateur accède au formulaire.",
            "étapes": ["Saisir un email valide.", "Soumettre le formulaire."],
            "données_fictives": {"email": "alice@example.com"},
            "résultat_attendu": "Compte créé avec succès.",
            "priorité": "high",
            "user_story": "US-006",
            "status": "à valider",
        },
        {
            "id": "TC-002",
            "titre": "Email invalide — format incorrect",
            "catégorie": "negative",
            "préconditions": "L'utilisateur accède au formulaire.",
            "étapes": ["Saisir 'not-an-email'.", "Soumettre le formulaire."],
            "données_fictives": {"email": "not-an-email"},
            "résultat_attendu": "Message d'erreur : format email invalide.",
            "priorité": "high",
            "user_story": "US-006",
            "status": "à valider",
        },
    ],
    "ambiguities": [],
    "sources": ["US-006"],
    "warnings": [],
    "requires_human_validation": True,
}

_AGENT_OUT_OF_SCOPE = {
    "status": "out_of_scope",
    "intent": "out_of_scope",
    "answer": "Je suis spécialisé en QA logicielle.",
    "test_cases": [],
    "ambiguities": [],
    "sources": [],
    "warnings": [],
    "requires_human_validation": False,
}


@pytest.fixture()
def app():
    """Retourne l'app FastAPI après avoir mocké is_indexed (évite ChromaDB au démarrage)."""
    with patch("api.is_indexed", return_value=True):
        from api import app as fastapi_app
        return fastapi_app


@pytest.fixture()
async def client(app):
    """Client HTTP asynchrone pour les tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ══════════════════════════════════════════════════════════════════════════════
# GET /health
# ══════════════════════════════════════════════════════════════════════════════

async def test_health_ok(client):
    with patch("api.is_indexed", return_value=True):
        r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["rag_indexed"] is True
    assert "model" in data
    assert "version" in data


async def test_health_rag_not_indexed(client):
    with patch("api.is_indexed", return_value=False):
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["rag_indexed"] is False


# ══════════════════════════════════════════════════════════════════════════════
# GET /metrics
# ══════════════════════════════════════════════════════════════════════════════

async def test_metrics_initial(client):
    """Les métriques démarrent à zéro (ou proches)."""
    r = await client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "requests_total" in data
    assert "avg_response_time_ms" in data
    assert "test_cases_generated" in data


# ══════════════════════════════════════════════════════════════════════════════
# POST /ask — validation des entrées
# ══════════════════════════════════════════════════════════════════════════════

async def test_ask_empty_question(client):
    """Une question vide doit renvoyer 422 (Pydantic validation)."""
    r = await client.post("/ask", json={"question": ""})
    assert r.status_code == 422


async def test_ask_blank_question(client):
    """Une question avec seulement des espaces doit renvoyer 422."""
    r = await client.post("/ask", json={"question": "   "})
    assert r.status_code == 422


async def test_ask_too_long_question(client):
    """Une question de plus de 5000 chars doit renvoyer 422."""
    r = await client.post("/ask", json={"question": "x" * 5001})
    assert r.status_code == 422


async def test_ask_missing_question_field(client):
    """Un corps sans 'question' doit renvoyer 422."""
    r = await client.post("/ask", json={})
    assert r.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# POST /ask — réponses valides
# ══════════════════════════════════════════════════════════════════════════════

async def test_ask_success_generates_test_cases(client):
    """Une requête valide doit retourner status=success et des test_cases."""
    with patch("api.agent", return_value=_AGENT_SUCCESS):
        r = await client.post("/ask", json={"question": "Generate test cases for US-006"})

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["intent"] == "generate_tests"
    assert len(data["test_cases"]) == 2
    assert data["requires_human_validation"] is True


async def test_ask_with_session_id(client):
    """Le session_id optionnel doit être accepté sans erreur."""
    with patch("api.agent", return_value=_AGENT_SUCCESS):
        r = await client.post("/ask", json={
            "question": "Generate test cases for US-006",
            "session_id": "abc-123",
        })
    assert r.status_code == 200


async def test_ask_out_of_scope(client):
    """Une question hors-scope doit retourner status=out_of_scope."""
    with patch("api.agent", return_value=_AGENT_OUT_OF_SCOPE):
        r = await client.post("/ask", json={"question": "Quelle est la capitale de la France ?"})
    assert r.status_code == 200
    assert r.json()["status"] == "out_of_scope"
    assert r.json()["test_cases"] == []


async def test_ask_updates_metrics(client):
    """Chaque appel à /ask doit incrémenter requests_total."""
    # Récupérer l'état initial
    m_before = (await client.get("/metrics")).json()

    with patch("api.agent", return_value=_AGENT_SUCCESS):
        await client.post("/ask", json={"question": "Generate test cases for US-006"})

    m_after = (await client.get("/metrics")).json()
    assert m_after["requests_total"] > m_before["requests_total"]
    assert m_after["test_cases_generated"] >= m_before["test_cases_generated"] + 2


async def test_ask_agent_exception_returns_500(client):
    """Si agent() lève une exception inattendue, l'API doit renvoyer 500."""
    with patch("api.agent", side_effect=RuntimeError("LLM unavailable")):
        r = await client.post("/ask", json={"question": "Generate test cases for US-006"})
    assert r.status_code == 500


# ══════════════════════════════════════════════════════════════════════════════
# Swagger / OpenAPI
# ══════════════════════════════════════════════════════════════════════════════

async def test_openapi_schema_accessible(client):
    """Le schéma OpenAPI doit être accessible."""
    r = await client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "/ask" in schema["paths"]
    assert "/health" in schema["paths"]
    assert "/metrics" in schema["paths"]


async def test_docs_accessible(client):
    """La documentation Swagger UI doit être accessible."""
    r = await client.get("/docs")
    assert r.status_code == 200
