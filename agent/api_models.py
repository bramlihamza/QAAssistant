"""
api_models.py — Modèles Pydantic pour l'API FastAPI du QA Assistant.

Validation stricte des entrées/sorties via Pydantic v2.
"""

from typing import Any
from pydantic import BaseModel, Field, field_validator


# ── Requête ───────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    """Corps de la requête POST /ask."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Question ou instruction pour l'agent QA (max 5000 caractères).",
        examples=["Generate test cases for US-006"],
    )
    session_id: str | None = Field(
        default=None,
        description="Identifiant de session optionnel pour tracer les échanges.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La question ne peut pas être vide ou uniquement des espaces.")
        return v.strip()


# ── Cas de test ───────────────────────────────────────────────────────────────

class TestCase(BaseModel):
    """Un cas de test généré par l'agent."""

    id: str = Field(..., description="Identifiant unique du cas de test (ex: TC-001).")
    titre: str = Field(..., description="Titre court et descriptif du cas de test.")
    categorie: str = Field(
        ...,
        alias="catégorie",
        description="Catégorie du test : positive | negative | limite.",
    )
    preconditions: str = Field(
        ...,
        alias="préconditions",
        description="Conditions requises avant l'exécution du test.",
    )
    etapes: list[str] = Field(
        ...,
        alias="étapes",
        description="Étapes ordonnées à suivre pour exécuter le test.",
    )
    donnees_fictives: dict[str, Any] = Field(
        default_factory=dict,
        alias="données_fictives",
        description="Données de test réalistes et fictives (jamais de données réelles).",
    )
    resultat_attendu: str = Field(
        ...,
        alias="résultat_attendu",
        description="Comportement attendu après l'exécution du test.",
    )
    priorite: str = Field(
        ...,
        alias="priorité",
        description="Priorité du test : high | medium | low.",
    )
    user_story: str = Field(..., description="Index de la user story source (ex: US-006).")
    status: str = Field(
        default="à valider",
        description="Statut du cas de test.",
    )

    model_config = {"populate_by_name": True}


# ── Réponse ───────────────────────────────────────────────────────────────────

class AskResponse(BaseModel):
    """Corps de la réponse POST /ask."""

    status: str = Field(
        ...,
        description="Statut de la réponse : success | error | clarification_needed | out_of_scope.",
    )
    intent: str = Field(
        ...,
        description="Intention détectée : generate_tests | analyze_story | detect_ambiguities | general | out_of_scope.",
    )
    answer: str = Field(..., description="Résumé en langage naturel de la réponse.")
    test_cases: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Cas de test générés (vide si intent non QA).",
    )
    ambiguities: list[str] = Field(
        default_factory=list,
        description="Ambiguïtés ou manques détectés dans les user stories.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Identifiants des user stories analysées (ex: ['US-006']).",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Avertissements non bloquants (données filtrées, validations partielles…).",
    )
    requires_human_validation: bool = Field(
        default=True,
        description="Toujours True — les cas de test générés doivent être validés par un humain.",
    )


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Corps de la réponse GET /health."""

    status: str = Field(default="ok", description="Statut de santé de l'API.")
    rag_indexed: bool = Field(..., description="True si la base vectorielle ChromaDB est peuplée.")
    model: str = Field(..., description="Modèle LLM utilisé.")
    version: str = Field(default="0.5.0", description="Version de l'API.")


# ── Metrics ───────────────────────────────────────────────────────────────────

class MetricsResponse(BaseModel):
    """Corps de la réponse GET /metrics."""

    requests_total: int = Field(..., description="Nombre total de requêtes /ask reçues depuis le démarrage.")
    requests_success: int = Field(..., description="Nombre de requêtes avec status='success'.")
    requests_error: int = Field(..., description="Nombre de requêtes avec status='error'.")
    avg_response_time_ms: float = Field(..., description="Temps de réponse moyen en millisecondes.")
    test_cases_generated: int = Field(..., description="Nombre total de cas de test générés.")
