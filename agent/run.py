"""
run.py — Point d'entrée uvicorn pour le QA Assistant API.

Usage :
  uv run python run.py                  # dev (reload automatique)
  uv run python run.py --host 0.0.0.0   # accessible depuis le réseau local

Ou directement :
  uv run uvicorn api:app --reload
"""

import argparse
import logging

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="QA Assistant API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse d'écoute (défaut : 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port d'écoute (défaut : 8000)")
    parser.add_argument("--reload", action="store_true", default=True, help="Rechargement automatique en dev")
    parser.add_argument("--no-reload", dest="reload", action="store_false", help="Désactiver le reload (prod)")
    args = parser.parse_args()

    print(f"\n🚀 QA Assistant API démarré")
    print(f"   URL : http://{args.host}:{args.port}")
    print(f"   Docs : http://{args.host}:{args.port}/docs")
    print(f"   Reload : {'activé' if args.reload else 'désactivé'}\n")

    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
