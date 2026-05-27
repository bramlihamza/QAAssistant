"""
scripts/evaluate_rag.py — Évaluation qualité du pipeline RAG + agent QA.

Utilise RAGAS pour évaluer automatiquement :
  - context_precision  : les chunks RAG récupérés sont-ils pertinents ?
  - faithfulness       : la réponse de l'agent est-elle fidèle aux sources ?
  - answer_relevancy   : la réponse est-elle pertinente à la question ?
  - context_recall     : le contexte RAG couvre-t-il la réponse attendue ?

Usage :
  uv run python scripts/evaluate_rag.py              # rapport console
  uv run python scripts/evaluate_rag.py --out report.json  # export JSON

Coût estimé : ~0.02–0.05 $ (5 questions × GPT-4o-mini juge)
"""

import argparse
import json
import logging
import sys
import os

# Ajouter le répertoire agent/ au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ── Dataset d'évaluation ─────────────────────────────────────────────────────
# Chaque sample : question QA → contextes RAG récupérés dynamiquement
#               → réponse agent → réponse de référence (ground_truth)
_EVAL_SAMPLES = [
    {
        "question": "What ISTQB technique should I use to test email format validation?",
        "ground_truth": (
            "Equivalence Partitioning should be used to partition inputs into valid "
            "(correct email format) and invalid classes (missing @, missing domain, etc.). "
            "Boundary Value Analysis can be applied to test maximum email length."
        ),
    },
    {
        "question": "How should I test minimum and maximum password length boundaries?",
        "ground_truth": (
            "Boundary Value Analysis (BVA) should be applied: test the exact minimum length, "
            "one character below the minimum, the exact maximum, and one above the maximum. "
            "This ensures boundary conditions are correctly handled."
        ),
    },
    {
        "question": "What testing techniques apply to form submission with mandatory and optional fields?",
        "ground_truth": (
            "Decision Table Testing is the most appropriate technique when multiple input conditions "
            "combine to produce different outcomes. Each combination of mandatory/optional fields "
            "filled or empty defines a rule in the decision table."
        ),
    },
    {
        "question": "How to create negative test cases for user account creation?",
        "ground_truth": (
            "Negative test cases should cover: invalid email format, duplicate email, "
            "password too short, password without required characters, "
            "empty mandatory fields, and SQL injection attempts. "
            "Error Guessing technique helps identify these based on tester experience."
        ),
    },
    {
        "question": "What is the difference between verification and validation in software testing?",
        "ground_truth": (
            "Verification checks whether the product is built correctly (are we building the product right?), "
            "while validation checks whether the correct product is built (are we building the right product?). "
            "Verification is typically done without executing the code (static testing), "
            "validation involves executing the software (dynamic testing)."
        ),
    },
]


def _retrieve_context(question: str) -> list[str]:
    """Récupère les chunks ISTQB pertinents pour une question."""
    from rag.retrieve import retrieve
    chunks = retrieve(question)
    return [c.content for c in chunks]


def _get_agent_answer(question: str) -> str:
    """
    Génère une réponse de l'agent pour une question.

    Pour l'évaluation, on appelle l'agent en mode 'général' (sans fetch US)
    afin d'évaluer uniquement la qualité du pipeline RAG.
    """
    from llm import call_llm_json
    from rag.retrieve import retrieve, build_rag_context

    # Récupérer le contexte RAG
    chunks = retrieve(question)
    rag_ctx = build_rag_context(chunks)

    # Construire un prompt simple d'évaluation
    from prompts_loader import load_system_prompt
    messages = [
        {"role": "system", "content": (
            "You are an expert software QA engineer. "
            "Answer the following question about testing techniques "
            "based on the ISTQB knowledge base provided.\n\n"
            + (f"ISTQB Context:\n{rag_ctx}" if rag_ctx else "No context retrieved.")
        )},
        {"role": "user", "content": question},
    ]

    try:
        from llm import call_llm
        return call_llm(messages)
    except Exception as e:
        logger.error("Erreur LLM pour '%s': %s", question[:50], e)
        return ""


def _load_system_prompt() -> str:
    """Charge le prompt système."""
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
    with open(os.path.join(prompts_dir, "system.md"), encoding="utf-8") as f:
        return f.read()


def build_dataset() -> list[dict]:
    """
    Construit le dataset RAGAS en récupérant dynamiquement
    les contextes RAG et les réponses agent pour chaque sample.
    """
    print("\n🔍 Construction du dataset d'évaluation...")
    samples = []

    for i, s in enumerate(_EVAL_SAMPLES, 1):
        question = s["question"]
        print(f"  [{i}/{len(_EVAL_SAMPLES)}] {question[:70]}...")

        contexts = _retrieve_context(question)
        if not contexts:
            print(f"    ⚠️  Aucun chunk RAG récupéré — question ignorée.")
            continue

        # Appel LLM pour la réponse agent
        from llm import call_llm
        from rag.retrieve import retrieve, build_rag_context
        chunks = retrieve(question)
        rag_ctx = build_rag_context(chunks)

        messages = [
            {"role": "system", "content": (
                "You are an expert software QA engineer. "
                "Answer the following question based on ISTQB best practices.\n\n"
                + (f"Context:\n{rag_ctx}" if rag_ctx else "")
            )},
            {"role": "user", "content": question},
        ]
        try:
            answer = call_llm(messages)
        except Exception as e:
            print(f"    ⚠️  Erreur LLM : {e}")
            continue

        samples.append({
            "user_input": question,
            "retrieved_contexts": contexts,
            "response": answer,
            "reference": s["ground_truth"],
        })
        print(f"    ✅ {len(contexts)} chunks | réponse: {len(answer)} chars")

    return samples


def run_evaluation(samples: list[dict]) -> dict:
    """Lance l'évaluation RAGAS sur les samples préparés."""
    from ragas import evaluate
    from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
    from ragas.metrics import (
        LLMContextPrecisionWithReference,
        Faithfulness,
        ResponseRelevancy,
        LLMContextRecall,
    )
    from ragas.llms import LangchainLLMWrapper
    from langchain_openai import ChatOpenAI
    from config import OPENAI_API_KEY, MODEL

    print("\n⚖️  Évaluation RAGAS en cours...")

    # LLM juge (même modèle que l'agent)
    judge_llm = LangchainLLMWrapper(ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL,
        temperature=0,
    ))

    # Construire le dataset RAGAS
    ragas_samples = [
        SingleTurnSample(
            user_input=s["user_input"],
            retrieved_contexts=s["retrieved_contexts"],
            response=s["response"],
            reference=s["reference"],
        )
        for s in samples
    ]
    dataset = EvaluationDataset(samples=ragas_samples)

    # Métriques à évaluer
    metrics = [
        LLMContextPrecisionWithReference(),  # chunks pertinents ?
        Faithfulness(),                       # réponse fidèle aux sources ?
        ResponseRelevancy(),                  # réponse pertinente à la question ?
        LLMContextRecall(),                   # contexte couvre la ground_truth ?
    ]

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=judge_llm,
        raise_exceptions=False,
    )

    return result


def print_report(result, samples: list[dict]) -> dict:
    """Affiche et retourne le rapport d'évaluation."""
    print("\n" + "═" * 60)
    print("  📊  RAPPORT D'ÉVALUATION RAG — QA Assistant")
    print("═" * 60)

    # Scores globaux
    score_map = {
        "context_precision":    ("LLMContextPrecisionWithReference", "Précision du contexte RAG"),
        "faithfulness":         ("Faithfulness",                     "Fidélité aux sources"),
        "answer_relevancy":     ("ResponseRelevancy",                "Pertinence de la réponse"),
        "context_recall":       ("LLMContextRecall",                 "Rappel du contexte"),
    }

    scores = {}
    df = result.to_pandas()

    for key, (col_name, label) in score_map.items():
        # Cherche la colonne (noms variables selon version RAGAS)
        col = next((c for c in df.columns if col_name.lower() in c.lower()), None)
        if col:
            val = float(df[col].mean())
            scores[key] = round(val, 3)
            bar = "█" * int(val * 20) + "░" * (20 - int(val * 20))
            print(f"  {label:<35} {bar}  {val:.3f}")
        else:
            scores[key] = None
            print(f"  {label:<35} (non disponible)")

    print("─" * 60)
    available = [v for v in scores.values() if v is not None]
    global_score = sum(available) / len(available) if available else 0.0
    print(f"  {'Score global':<35} {'★' * int(global_score * 5)}    {global_score:.3f}")
    print("═" * 60)

    # Détail par question
    print("\n  Détail par question :\n")
    for i, sample in enumerate(samples):
        q = sample["user_input"][:60]
        print(f"  [{i+1}] {q}...")
        if i < len(df):
            row = df.iloc[i]
            for key, (col_name, _) in score_map.items():
                col = next((c for c in df.columns if col_name.lower() in c.lower()), None)
                if col and col in row:
                    val = row[col]
                    print(f"      {key:<25} {val:.3f}" if isinstance(val, float) else f"      {key:<25} N/A")
        print()

    return {
        "scores": scores,
        "global_score": round(global_score, 3),
        "n_samples": len(samples),
        "model": "gpt-4o-mini",
    }


def main():
    parser = argparse.ArgumentParser(description="Évaluation qualité du pipeline RAG — QA Assistant")
    parser.add_argument("--out", metavar="FILE", help="Exporter le rapport en JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Affiche le dataset sans appeler RAGAS (vérifie le RAG uniquement)")
    args = parser.parse_args()

    print("🚀 QA Assistant — Évaluation RAGAS")
    print(f"   Dataset : {len(_EVAL_SAMPLES)} questions ISTQB")
    mode_label = "dry-run (pas d'appel RAGAS)" if args.dry_run else "évaluation complète"
    print(f"   Mode    : {mode_label}")

    # 1. Construire le dataset
    samples = build_dataset()
    if not samples:
        print("\n❌ Aucun sample construit — vérifiez que ChromaDB est indexé.")
        print("   Lancez : uv run python scripts/ingest_docs.py")
        sys.exit(1)

    print(f"\n✅ {len(samples)}/{len(_EVAL_SAMPLES)} samples prêts.")

    if args.dry_run:
        print("\n[dry-run] Contextes récupérés :")
        for i, s in enumerate(samples, 1):
            print(f"  [{i}] Q: {s['user_input'][:60]}...")
            print(f"       {len(s['retrieved_contexts'])} chunks | réponse: {s['response'][:80]}...")
        return

    # 2. Évaluer
    result = run_evaluation(samples)

    # 3. Rapport
    report = print_report(result, samples)

    # 4. Export JSON optionnel
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Rapport exporté : {args.out}")


if __name__ == "__main__":
    main()
