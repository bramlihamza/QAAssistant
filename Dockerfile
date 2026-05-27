# ── Étape 1 : build des dépendances ──────────────────────────────────────────
FROM python:3.11-slim AS builder

# Installer uv (gestionnaire de paquets)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copier uniquement les fichiers de dépendances pour profiter du cache Docker
COPY agent/pyproject.toml agent/uv.lock ./

# Installer les dépendances dans un venv isolé (sans les dev deps)
RUN uv sync --frozen --no-dev --no-install-project


# ── Étape 2 : image finale ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Métadonnées
LABEL maintainer="QA Assistant"
LABEL description="Agent IA QA — génération de cas de test ISTQB via FastAPI"
LABEL version="0.7.0"

WORKDIR /app

# Récupérer le venv construit à l'étape précédente
COPY --from=builder /app/.venv /app/.venv

# Copier le code de l'application
COPY agent/ .

# PDFs ISTQB — fournis via un volume monté sur /pdf
# Sur Railway, attacher un volume au chemin /pdf
RUN mkdir -p /pdf

# Variable d'environnement pour utiliser le venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Pointer vers les PDFs copiés dans l'image
ENV ISTQB_DOCS_DIR=/pdf

# ChromaDB persisté dans un volume Docker
# Monter avec : -v qa_chroma:/app/chroma_db
ENV CHROMA_PERSIST_DIR=/app/chroma_db

# Port de l'API FastAPI
EXPOSE 8000

# Démarrage de l'API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
