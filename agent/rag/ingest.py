"""
rag/ingest.py — Chargement et extraction du texte des PDFs ISTQB.

Utilise PyMuPDF (fitz) pour extraire le texte page par page
avec les métadonnées nécessaires au retrieval (source, page, langue).

Documents supportés :
  - ISTQB CTFL v4.0.1          (anglais, 78 pages)
  - ISTQB CTAL-TA v4.0 FR      (français, 81 pages)
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

# ── Mapping des fichiers PDF connus ──────────────────────────────────────────
_KNOWN_DOCS: dict[str, dict] = {
    "ISTQB_CTFL_Syllabus_v4.0.1.pdf": {
        "label": "ISTQB CTFL v4.0.1",
        "language": "en",
        "type": "Foundation Level",
    },
    "ISTQB-CTAL-TA-Syllabus-v4.0-FR_final.pdf": {
        "label": "ISTQB CTAL-TA v4.0 FR",
        "language": "fr",
        "type": "Advanced Level - Test Analyst",
    },
}

# Pages à ignorer : couverture, copyright, table des matières (généralement les 9 premières)
_SKIP_PAGES_BEFORE = 9


@dataclass
class RawPage:
    """Représente une page extraite d'un document ISTQB."""
    content: str
    metadata: dict = field(default_factory=dict)


def load_pdf(pdf_path: str | Path) -> list[RawPage]:
    """
    Extrait le texte d'un PDF page par page.

    Args:
        pdf_path: chemin absolu ou relatif vers le fichier PDF.

    Returns:
        Liste de RawPage avec le texte et les métadonnées.
    """
    path = Path(pdf_path)
    if not path.exists():
        logger.error("PDF introuvable : %s", path)
        return []

    filename = path.name
    doc_meta = _KNOWN_DOCS.get(filename, {
        "label": filename,
        "language": "unknown",
        "type": "unknown",
    })

    pages: list[RawPage] = []
    try:
        doc = fitz.open(str(path))
        total_pages = doc.page_count
        logger.info("Chargement PDF : %s (%d pages)", doc_meta["label"], total_pages)

        for page_num in range(total_pages):
            # Ignorer les pages préliminaires (couverture, copyright, ToC)
            if page_num < _SKIP_PAGES_BEFORE:
                continue

            text = doc[page_num].get_text().strip()
            if not text or len(text) < 100:  # ignorer les pages vides ou trop courtes
                continue

            pages.append(RawPage(
                content=text,
                metadata={
                    "source": doc_meta["label"],
                    "filename": filename,
                    "language": doc_meta["language"],
                    "doc_type": doc_meta["type"],
                    "page": page_num + 1,
                },
            ))

        doc.close()
        logger.info("Pages extraites : %d / %d", len(pages), total_pages)

    except Exception as e:
        logger.error("Erreur lors de l'extraction de %s : %s", path, e)

    return pages


def load_all_pdfs(docs_dir: str | Path) -> list[RawPage]:
    """
    Charge tous les PDFs ISTQB depuis un répertoire.

    Args:
        docs_dir: répertoire contenant les fichiers PDF.

    Returns:
        Liste concaténée de toutes les RawPage extraites.
    """
    docs_dir = Path(docs_dir)
    if not docs_dir.exists():
        logger.error("Répertoire de documents introuvable : %s", docs_dir)
        return []

    all_pages: list[RawPage] = []
    pdf_files = sorted(docs_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning("Aucun PDF trouvé dans : %s", docs_dir)
        return []

    for pdf_path in pdf_files:
        pages = load_pdf(pdf_path)
        all_pages.extend(pages)
        logger.info("  → %s : %d pages chargées", pdf_path.name, len(pages))

    logger.info("Total pages chargées : %d", len(all_pages))
    return all_pages
