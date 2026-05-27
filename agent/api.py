"""
api.py — Application FastAPI du QA Assistant.

Endpoints :
  POST /ask     → soumet une question à l'agent QA
  GET  /health  → vérifie l'état de l'API et du RAG
  GET  /metrics → statistiques d'utilisation depuis le démarrage

Documentation interactive : http://localhost:8000/docs
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api_models import AskRequest, AskResponse, HealthResponse, MetricsResponse
from config import MODEL
from main import agent
from rag.vector_store import is_indexed

logger = logging.getLogger(__name__)

# ── Compteurs in-memory (reset à chaque redémarrage) ─────────────────────────
_metrics: dict = {
    "requests_total": 0,
    "requests_success": 0,
    "requests_error": 0,
    "response_times_ms": [],   # liste des derniers temps de réponse (max 1000)
    "test_cases_generated": 0,
}

_MAX_RESPONSE_TIMES = 1000  # évite une croissance illimitée


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Tâches au démarrage / à l'arrêt de l'application.
    Vérifie que la base vectorielle est accessible.
    """
    logger.info("🚀 Démarrage du QA Assistant API")
    if not is_indexed():
        logger.warning(
            "⚠️  La base vectorielle ChromaDB n'est pas peuplée. "
            "Lancez : uv run python scripts/ingest_docs.py"
        )
    else:
        logger.info("✅ ChromaDB opérationnelle.")
    yield
    logger.info("🛑 Arrêt du QA Assistant API")


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="QA Assistant API",
    description=(
        "Agent IA spécialisé en assurance qualité logicielle.\n\n"
        "Génère des cas de test fonctionnels à partir de user stories, "
        "enrichis par les bonnes pratiques ISTQB (CTFL v4.0.1 + CTAL-TA v4.0 FR)."
    ),
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — autorise toutes les origines en développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Gestionnaire d'erreurs global ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Erreur non gérée sur %s : %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erreur interne du serveur. Consultez les logs pour plus de détails.",
            "type": type(exc).__name__,
        },
    )


# ── POST /ask ─────────────────────────────────────────────────────────────────

@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Soumettre une question à l'agent QA",
    description=(
        "Analyse la question, détecte l'intention, récupère les user stories, "
        "enrichit avec les bonnes pratiques ISTQB et génère des cas de test."
    ),
    tags=["Agent"],
)
async def ask(body: AskRequest) -> AskResponse:
    """
    Point d'entrée principal de l'agent QA.

    - **question** : question ou instruction (max 5000 chars)
    - **session_id** : optionnel, pour tracer les échanges
    """
    start_time = time.perf_counter()
    _metrics["requests_total"] += 1

    logger.info(
        "POST /ask — session_id=%s, question='%s...'",
        body.session_id or "N/A",
        body.question[:80],
    )

    try:
        result = agent(body.question)
    except Exception as e:
        _metrics["requests_error"] += 1
        logger.error("Erreur dans agent() : %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement de la requête : {type(e).__name__}",
        ) from e

    # Mise à jour des métriques
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    _metrics["response_times_ms"].append(elapsed_ms)
    if len(_metrics["response_times_ms"]) > _MAX_RESPONSE_TIMES:
        _metrics["response_times_ms"] = _metrics["response_times_ms"][-_MAX_RESPONSE_TIMES:]

    if result.get("status") == "success":
        _metrics["requests_success"] += 1
    else:
        _metrics["requests_error"] += 1

    tc_count = len(result.get("test_cases", []))
    _metrics["test_cases_generated"] += tc_count

    logger.info(
        "POST /ask terminé — status=%s, test_cases=%d, durée=%.0fms",
        result.get("status"),
        tc_count,
        elapsed_ms,
    )

    return AskResponse(**result)


# ── GET /health ───────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Vérifier l'état de santé de l'API",
    description="Retourne l'état de l'API, du modèle LLM et de la base vectorielle ChromaDB.",
    tags=["Monitoring"],
)
async def health() -> HealthResponse:
    """Vérification de l'état de santé."""
    try:
        indexed = is_indexed()
    except Exception as e:
        logger.warning("Erreur lors de la vérification ChromaDB : %s", e)
        indexed = False

    return HealthResponse(
        status="ok",
        rag_indexed=indexed,
        model=MODEL,
        version="0.5.0",
    )


# ── GET /metrics ──────────────────────────────────────────────────────────────

@app.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Statistiques d'utilisation de l'API",
    description="Compteurs et temps de réponse depuis le dernier démarrage du serveur.",
    tags=["Monitoring"],
)
async def metrics() -> MetricsResponse:
    """Métriques d'utilisation in-memory."""
    times = _metrics["response_times_ms"]
    avg_ms = sum(times) / len(times) if times else 0.0

    return MetricsResponse(
        requests_total=_metrics["requests_total"],
        requests_success=_metrics["requests_success"],
        requests_error=_metrics["requests_error"],
        avg_response_time_ms=round(avg_ms, 1),
        test_cases_generated=_metrics["test_cases_generated"],
    )
