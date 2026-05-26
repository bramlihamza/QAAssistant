# Guide d'implémentation - Assistant IA solide

**Objectif :** reprendre l'ensemble des étapes nécessaires pour concevoir, implémenter, tester, sécuriser, déployer et monitorer un assistant IA robuste en contexte professionnel.

Ce guide consolide les apports des modules fournis : fondamentaux LLM, conception fonctionnelle, architecture agent, prototypage Python, RAG, intégration SI, tests, Docker, déploiement, monitoring, KPIs et conduite du changement.

---

## 1. Cadrer le besoin métier avant de coder

Un assistant solide commence par un problème métier clair, mesurable et utile.

### Étapes

1. Identifier le processus cible.
2. Mesurer le volume actuel.
3. Estimer le temps passé par occurrence.
4. Quantifier le coût actuel.
5. Décrire les irritants métier.
6. Vérifier que l'automatisation apporte une valeur réelle.
7. Vérifier que les données nécessaires existent et sont exploitables.

### Questions à poser

| Question | Réponse attendue |
|---|---|
| Quel processus l'assistant doit-il améliorer ? | Exemple : génération de cas de test à partir de user stories. |
| Combien de demandes sont traitées par jour ? | Volume moyen et pics. |
| Combien de temps prend le traitement manuel ? | Temps moyen par occurrence. |
| Quel gain attend-on ? | Temps, coût, qualité, couverture, satisfaction. |
| Quelles tâches restent humaines ? | Validation finale, arbitrage métier, décisions sensibles. |

### Livrable

Un problème métier formulé ainsi :

```md
Aujourd'hui, [population] réalise [tâche] manuellement, ce qui représente [volume] et [temps/coût].
L'assistant doit réduire [objectif quantifié] tout en garantissant [qualité/sécurité/conformité].
```

---

## 2. Définir le périmètre fonctionnel

Le périmètre évite de créer un assistant trop vague ou trop risqué.

### Périmètre inclus

- Cas d'usage couverts.
- Types de demandes acceptées.
- Données consultables.
- Actions autorisées.
- Formats de sortie attendus.
- Utilisateurs concernés.

### Périmètre exclu

- Actions critiques sans validation humaine.
- Données hors périmètre.
- Cas non couverts par la documentation.
- Décisions réglementaires, juridiques ou RH non supervisées.
- Exécution automatique irréversible sans garde-fou.

### Exemple pour un assistant QA

```md
Inclus :
- Analyse de user stories.
- Extraction de règles métier.
- Génération de cas de test positifs, négatifs et limites.
- Détection d'ambiguïtés.
- Export JSON.

Exclu :
- Validation finale sans QA.
- Exécution automatique des tests.
- Tests de performance, sécurité ou accessibilité avancée.
- Utilisation de données personnelles réelles.
```

---

## 3. Choisir la bonne stratégie IA

Un assistant robuste ne commence pas forcément par du fine-tuning.

### Ordre recommandé

| Niveau | Usage | Quand l'utiliser |
|---|---|---|
| Prompt engineering | Rapide, flexible, sans infrastructure | Toujours commencer par là. |
| RAG | Réponses ancrées dans des documents internes | Dès que l'assistant doit répondre à partir d'une base métier. |
| Fine-tuning | Spécialisation profonde | Seulement pour des tâches très spécifiques, récurrentes et à fort volume. |

### Règle pratique

```md
Commencer par un bon prompt.
Ajouter du RAG si l'assistant doit utiliser des connaissances internes.
N'envisager le fine-tuning que si le prompt + RAG ne suffisent pas.
```

---

## 4. Comprendre les limites des LLM

Un assistant solide est conçu en tenant compte des limites des modèles.

### Risques à anticiper

| Risque | Impact | Réduction |
|---|---|---|
| Hallucination | Réponse fausse mais convaincante | RAG, sources, refus hors contexte, LLM-as-Judge. |
| Biais | Réponses orientées ou incomplètes | Validation humaine, jeux de test variés. |
| Fenêtre de contexte limitée | Perte d'information ancienne | Résumé, mémoire contrôlée, retrieval sélectif. |
| Coût token | Coûts élevés en production | Chunking, prompts courts, modèles adaptés par tâche. |
| Non-déterminisme | Réponses variables | Tests spécifiques, température basse, sorties structurées. |

### Bonnes pratiques

- Utiliser une température faible pour les tâches factuelles.
- Limiter le contexte injecté aux passages utiles.
- Demander au modèle de dire quand l'information est absente.
- Forcer les sorties structurées pour les traitements automatiques.
- Prévoir une validation humaine sur les décisions importantes.

---

## 5. Rédiger le cahier des charges fonctionnel

Le cahier des charges aligne le métier, la QA, l'IT et les sponsors.

### Structure minimale

1. Problème métier.
2. Objectifs mesurables.
3. Utilisateurs cibles.
4. Cas d'usage.
5. Entrées acceptées.
6. Sorties produites.
7. Cas d'erreur.
8. Données nécessaires.
9. KPIs.
10. Contraintes de sécurité et RGPD.
11. Critères d'acceptation du MVP.
12. Décision go/no-go.

### Exemple d'objectifs

```md
Objectif principal : proposer automatiquement des cas de test fonctionnels structurés à partir d'une user story.

Objectifs mesurables :
- Réduire de 40 % le temps de rédaction initiale.
- Atteindre 90 % de couverture des critères d'acceptation.
- Obtenir moins de 20 % de retouches majeures QA.
```

---

## 6. Définir les utilisateurs et les responsabilités

Un assistant IA d'entreprise doit être pensé comme un outil intégré dans un workflow humain.

| Profil | Rôle | Interaction avec l'assistant |
|---|---|---|
| Métier / Product Owner | Clarifie les règles métier | Soumet les besoins, valide les hypothèses. |
| QA / Validation | Contrôle la qualité | Relit, corrige et valide les sorties. |
| Développeur | Vérifie la cohérence technique | Consulte les cas limites et les comportements attendus. |
| Architecte / IT | Intègre et sécurise | Gère APIs, droits d'accès, déploiement. |
| DPO / Juridique | Valide la conformité | Vérifie RGPD, conservation, traçabilité. |
| Sponsor | Arbitre budget et ROI | Décide du passage en production. |

---

## 7. Concevoir l'architecture en 7 couches

Une architecture robuste sépare clairement les responsabilités.

| Couche | Rôle | Implémentation attendue |
|---|---|---|
| 1. Perception / Entrée | Recevoir et structurer les inputs | API, formulaire, chat, email, webhook, parsing, nettoyage. |
| 2. Orchestration | Piloter le workflow | Classification d'intention, choix du parcours, routing. |
| 3. Raisonnement LLM | Analyser et décider | Prompt métier, ReAct, génération structurée. |
| 4. Mémoire | Maintenir le contexte | Mémoire courte, mémoire longue, historique, préférences. |
| 5. Outils | Agir sur le SI | RAG, base de données, CRM, Jira, Slack, export JSON/CSV. |
| 6. Contrôle / Gouvernance | Sécuriser et tracer | RBAC, logs, RGPD, validation humaine, anti-hallucination. |
| 7. Sortie | Restituer proprement | JSON, réponse texte, rapport, statut, erreurs explicites. |

---

## 8. Structurer le projet Python

Une base propre facilite les tests, la maintenance et le déploiement.

### Arborescence recommandée

```txt
agent/
├── api.py                    # FastAPI : endpoints /ask, /health, /metrics
├── main.py                   # Orchestration principale de l'agent
├── llm.py                    # Abstraction multi-provider LLM
├── config.py                 # Variables d'environnement et paramètres
├── prompts/
│   ├── system.md
│   ├── classify_intent.md
│   └── generate_answer.md
├── tools/
│   ├── rag.py
│   ├── database.py
│   ├── jira.py
│   ├── slack.py
│   └── validator.py
├── memory/
│   ├── short_term.py
│   └── long_term.py
├── rag/
│   ├── ingest.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── retrieve.py
├── security/
│   ├── input_guard.py
│   ├── output_filter.py
│   └── access_control.py
├── monitoring/
│   ├── metrics.py
│   └── logging_config.py
├── tests/
│   ├── test_tools.py
│   ├── test_memory.py
│   ├── test_integration.py
│   └── test_quality.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### Principes

- `main.py` orchestre mais ne contient pas toute la logique métier.
- `llm.py` centralise les appels aux modèles.
- `tools/` contient des fonctions simples, robustes et testables.
- `memory/` gère le contexte.
- `rag/` gère l'ingestion, l'indexation et le retrieval.
- `security/` contient les garde-fous.
- `tests/` couvre les briques déterministes et la qualité LLM.

---

## 9. Créer une abstraction LLM multi-provider

L'assistant ne doit pas dépendre directement d'un seul fournisseur.

### Objectifs

- Pouvoir changer de modèle sans réécrire l'agent.
- Centraliser les paramètres : modèle, température, max tokens.
- Gérer les erreurs API.
- Standardiser les réponses.
- Supporter les sorties JSON.

### Exemple

```python
# llm.py
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(messages, model="gpt-4o", temperature=0.2):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Erreur appel LLM: {e}")


def call_llm_json(messages, schema_hint, model="gpt-4o"):
    messages = messages + [
        {
            "role": "system",
            "content": f"Réponds uniquement en JSON valide selon ce schéma: {schema_hint}",
        }
    ]
    raw = call_llm(messages, model=model, temperature=0)
    return json.loads(raw)
```

---

## 10. Forcer les sorties structurées

Une sortie libre est difficile à exploiter automatiquement. Pour un assistant solide, les sorties critiques doivent être structurées.

### Exemple de contrat JSON

```json
{
  "status": "success",
  "intent": "generate_tests",
  "answer": "...",
  "items": [],
  "sources": [],
  "warnings": [],
  "requires_human_validation": true
}
```

### Règles

- Définir le schéma attendu dans le prompt système.
- Valider le JSON avant usage.
- Retourner une erreur contrôlée si le JSON est invalide.
- Ajouter un champ `requires_human_validation` pour les cas sensibles.

---

## 11. Implémenter le cycle d'agent

Un assistant robuste suit un cycle explicite.

### Cycle général

1. Recevoir la requête.
2. Valider et nettoyer l'input.
3. Identifier l'intention.
4. Choisir le workflow.
5. Récupérer le contexte utile.
6. Choisir le tool nécessaire.
7. Exécuter l'action.
8. Observer le résultat.
9. Générer la réponse.
10. Valider le format de sortie.
11. Journaliser l'interaction.
12. Retourner une réponse claire.

### Exemple simplifié

```python
# main.py
from llm import call_llm_json
from memory.short_term import store, recall
from tools.rag import search_documents
from tools.validator import validate_output


def classify_intent(query):
    result = call_llm_json(
        [
            {"role": "system", "content": "Classe l'intention utilisateur."},
            {"role": "user", "content": query},
        ],
        schema_hint='{"intent":"search|generate|general|clarify"}',
    )
    return result["intent"]


def agent(query):
    store({"role": "user", "content": query})

    intent = classify_intent(query)
    context = recall(limit=5)

    if intent in ["search", "generate"]:
        docs = search_documents(query)
    else:
        docs = []

    response = call_llm_json(
        [
            {"role": "system", "content": "Tu es un assistant métier fiable. Si l'information manque, demande une clarification."},
            {"role": "user", "content": query},
            {"role": "system", "content": f"Contexte conversation: {context}"},
            {"role": "system", "content": f"Documents utiles: {docs}"},
        ],
        schema_hint='{"status":"success|error","answer":"...","warnings":[],"sources":[]}',
    )

    validate_output(response)
    store({"role": "assistant", "content": response["answer"]})
    return response
```

---

## 12. Utiliser le pattern ReAct pour les tâches complexes

ReAct signifie **Reasoning + Acting**. L'agent alterne entre réflexion, choix d'outil, action, observation et réponse.

### Boucle ReAct

```txt
Question utilisateur
→ Analyse de l'intention
→ Choix de l'action
→ Appel d'un tool
→ Observation du résultat
→ Nouvelle action si nécessaire
→ Réponse finale structurée
```

### Quand l'utiliser

- L'assistant doit chercher dans plusieurs sources.
- L'assistant doit appeler des outils métier.
- La réponse dépend d'une observation externe.
- Le workflow nécessite plusieurs étapes.

### À éviter

- ReAct pour des questions très simples.
- Boucles sans limite.
- Actions critiques sans confirmation humaine.

### Garde-fous

- Nombre maximal d'itérations.
- Liste fermée de tools autorisés.
- Logs à chaque étape.
- Refus si aucun outil pertinent n'est disponible.

---

## 13. Concevoir des tools simples, documentés et robustes

Un mauvais tool est l'une des principales causes d'échec d'un agent.

### Template de spécification d'un tool

```md
NOM : rechercher_commande
DESCRIPTION : recherche une commande par numéro ou nom client.
ENTRÉES :
- numero_commande: string, optionnel
- nom_client: string, optionnel
SORTIE SUCCÈS :
- JSON { "statut": "...", "date": "...", "montant": 123.45 }
SORTIE ERREUR :
- JSON { "erreur": "...", "suggestion": "..." }
GESTION D'ERREUR :
- Introuvable : message explicite.
- API indisponible : retry 1 fois puis erreur contrôlée.
- Timeout > 5 secondes : abandon + message utilisateur.
```

### Critères d'un bon tool

| Critère | Description |
|---|---|
| Simple | Une fonction = une responsabilité. |
| Documenté | Description claire pour que le LLM sache quand l'appeler. |
| Robuste | Gestion des erreurs, timeouts et cas limites. |
| Testable | Peut être testé sans appeler le LLM. |
| Sécurisé | Droits d'accès et validation des entrées. |

### Exemple

```python
# tools/jira.py
import requests


def create_jira_ticket(title, description, api_key):
    try:
        response = requests.post(
            "https://jira.example.com/api/tickets",
            json={"title": title, "description": description},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5,
        )
        response.raise_for_status()
        return {"status": "success", "ticket": response.json()}
    except requests.Timeout:
        return {"status": "error", "message": "Timeout Jira"}
    except requests.HTTPError as e:
        return {"status": "error", "message": f"Erreur API Jira: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Erreur inattendue: {e}"}
```

---

## 14. Implémenter la mémoire

La mémoire permet à l'assistant de maintenir une conversation cohérente.

### Types de mémoire

| Type | Usage | Stockage possible |
|---|---|---|
| Mémoire courte | Historique de session | Liste Python, Redis, session DB. |
| Mémoire longue | Connaissances persistantes | Base vectorielle, SQL, fichiers JSON. |

### Mémoire courte simple

```python
# memory/short_term.py
memory = []
MAX_MEMORY = 10


def store(message):
    memory.append(message)
    del memory[:-MAX_MEMORY]


def recall(limit=5):
    return memory[-limit:]


def clear():
    memory.clear()
```

### Bonnes pratiques

- Stocker les rôles : `user`, `assistant`, `system`, `tool`.
- Limiter le nombre de messages rappelés.
- Résumer les conversations longues.
- Ne jamais stocker inutilement de données sensibles.
- Pour la mémoire longue, récupérer uniquement les souvenirs pertinents via similarité.

---

## 15. Construire le pipeline RAG

Le RAG rend l'assistant fiable sur les connaissances métier.

### Pipeline complet

```txt
Documents métier
→ Préparation des données
→ Ingestion
→ Chunking
→ Embeddings
→ Stockage vectoriel
→ Retrieval
→ Filtrage par score
→ Injection dans le prompt
→ Réponse sourcée
```

### Étape 1 - Préparer les données

| Format | Outils | Points d'attention |
|---|---|---|
| PDF | PyMuPDF, pdfplumber | PDF scannés, OCR, tableaux mal extraits. |
| CSV / Excel | pandas | Encodage, colonnes vides, doublons. |
| JSON | json natif | Champs manquants, structures imbriquées. |
| SQL | sqlite3, SQLAlchemy | Jointures, valeurs nulles, droits d'accès. |
| API | requests, httpx | Authentification, pagination, quotas. |

### Checklist avant ingestion

```md
- [ ] Fichiers lisibles et normalisés.
- [ ] Encodage UTF-8.
- [ ] Doublons supprimés.
- [ ] Données personnelles anonymisées.
- [ ] Documents obsolètes exclus.
- [ ] Métadonnées ajoutées : source, date, version, auteur.
- [ ] Accès validés par rôle.
```

### Étape 2 - Chunking

Recommandation : découper les documents en morceaux de **300 à 800 tokens** avec chevauchement.

Bonnes pratiques :

- Découper par titres, sections et paragraphes.
- Garder les métadonnées du document source.
- Éviter les chunks trop courts sans contexte.
- Éviter les chunks trop longs qui diluent l'information.

### Étape 3 - Embeddings

Les embeddings transforment le texte en vecteurs comparables par similarité.

```python
from openai import OpenAI
client = OpenAI()

embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Procédure de remboursement client"
)

vector = embedding.data[0].embedding
```

### Étape 4 - Stockage vectoriel

| Solution | Usage recommandé |
|---|---|
| FAISS | Prototypage local rapide. |
| Chroma | Démarrage simple avec interface Python. |
| Qdrant | Production, scalabilité, filtres avancés. |
| Pinecone | SaaS vectoriel managé. |

### Étape 5 - Retrieval

Récupérer les chunks les plus proches sémantiquement.

```python
results = vector_db.similarity_search(query, k=5)
```

### Étape 6 - Filtrer par score

```python
def retrieval_avec_seuil(query, k=5, seuil=0.70):
    results = vector_db.similarity_search_with_score(query, k=k)
    pertinents = [
        (doc, score)
        for doc, score in results
        if score >= seuil
    ]
    if not pertinents:
        return None, "Aucun document pertinent trouvé."
    return pertinents, None
```

### Interprétation des scores

| Score | Interprétation | Action |
|---|---|---|
| > 0.85 | Très pertinent | Injecter. |
| 0.70 - 0.85 | Pertinent | Injecter si utile. |
| 0.50 - 0.70 | Faiblement pertinent | Ignorer. |
| < 0.50 | Non pertinent | Ne pas injecter. |

### Étape 7 - Augmenter le prompt

```python
def build_rag_prompt(question, documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    return f"""
Tu es un assistant expert.
Réponds uniquement à partir du contexte fourni.
Si l'information n'est pas présente, dis-le clairement.

Contexte :
{context}

Question : {question}

Réponse :
"""
```

### Règles de fiabilité RAG

- Ne pas répondre si aucun document pertinent n'est trouvé.
- Citer les sources ou au minimum remonter leurs métadonnées.
- Versionner la base documentaire.
- Mesurer la qualité du retrieval.
- Tester avec des questions dans le corpus, hors corpus, reformulées et ambiguës.

---

## 16. Exposer l'assistant via API REST

FastAPI permet de rendre l'assistant consommable par une interface front, un SI, un chatbot ou un outil d'automatisation.

### Endpoints minimaux

| Endpoint | Rôle |
|---|---|
| `POST /ask` | Envoyer une requête à l'assistant. |
| `GET /health` | Vérifier que le service répond. |
| `GET /metrics` | Exposer les métriques de monitoring. |
| `POST /webhook/*` | Recevoir des événements métier. |

### Exemple FastAPI

```python
# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import agent
from monitoring.metrics import get_dashboard

app = FastAPI(title="Assistant IA")


class AskRequest(BaseModel):
    question: str
    user_id: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(payload: AskRequest):
    try:
        response = agent(payload.question)
        return {"status": "success", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    return get_dashboard()
```

### À prévoir

- Validation Pydantic des entrées.
- Authentification API key ou OAuth.
- Limitation de débit.
- Logs par requête.
- Documentation Swagger disponible sur `/docs`.

---

## 17. Connecter l'assistant au système d'information

Un assistant utile doit savoir et agir.

### Intégrations fréquentes

| Système | Actions possibles |
|---|---|
| Jira / Azure DevOps | Créer, lire, mettre à jour des tickets. |
| Confluence / SharePoint | Lire la documentation projet. |
| Slack / Teams | Envoyer une notification ou un résumé. |
| CRM | Lire / écrire des informations client. |
| Messagerie | Classer un email, générer un brouillon. |
| Base SQL | Lire des données métier contrôlées. |

### Workflow événementiel type

```txt
Email entrant
→ Webhook
→ Classification par l'assistant
→ Recherche documentaire RAG
→ Génération d'une réponse ou création d'un ticket
→ Notification Slack / Teams
→ Log + métriques
```

### Automatisation no-code possible

- n8n.
- Make.
- Zapier.

Ces outils sont utiles pour valider rapidement un workflow avant un développement plus industriel.

---

## 18. Implémenter la sécurité et la gouvernance

La sécurité est une architecture en couches, pas un seul contrôle.

### Garde-fous obligatoires

| Domaine | Mesures |
|---|---|
| Données | Anonymisation, pseudonymisation, minimisation. |
| Accès | RBAC, séparation des rôles, contrôle par source documentaire. |
| Prompt injection | Détection de patterns suspects, refus, sandbox tools. |
| Sorties | Filtrage des données sensibles, validation JSON. |
| Actions critiques | Validation humaine obligatoire. |
| Traçabilité | Logs des requêtes, réponses, outils appelés, sources. |
| Cycle de vie | Purge des données obsolètes, droit à l'oubli. |

### Validation des inputs

```python
# security/input_guard.py
import re

PATTERNS_INJECTION = [
    r"ignore\s+tes\s+instructions",
    r"tu\s+es\s+maintenant",
    r"system\s*prompt",
    r"repete.*tes\s+instructions",
]


def validate_input(question, max_len=5000):
    if not question or not question.strip():
        return False, "Question vide."

    question = question.strip()[:max_len]

    for pattern in PATTERNS_INJECTION:
        if re.search(pattern, question.lower()):
            return False, "Requête non autorisée."

    return True, question
```

### Filtrage des outputs

```python
# security/output_filter.py
import re

SENSIBLE = [
    (r"[\w.-]+@[\w.-]+\.\w+", "[EMAIL]"),
    (r"0[1-9]\s?\d{2}(\s?\d{2}){3}", "[TELEPHONE]"),
    (r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}", "[CARTE]"),
]


def filter_output(response):
    for pattern, mask in SENSIBLE:
        response = re.sub(pattern, mask, response)
    return response
```

---

## 19. Gérer les erreurs proprement

Un assistant solide ne doit pas planter silencieusement.

### Cas à gérer

- API indisponible.
- Timeout réseau.
- Quota dépassé.
- JSON invalide.
- Document introuvable.
- Aucun résultat RAG pertinent.
- Tool indisponible.
- Requête hors périmètre.
- Données sensibles détectées.

### Exemple

```python
try:
    result = call_api()
except TimeoutError:
    log_error("Timeout API")
    return "Service momentanément indisponible. Réessayez plus tard."
except ValueError as e:
    log_error(f"Données invalides: {e}")
    return "Erreur de format. Vérifiez les données envoyées."
except Exception as e:
    log_error(e)
    return "Erreur temporaire. L'équipe technique a été notifiée."
```

### Principes

- Toujours retourner un message explicite.
- Ne pas exposer les détails techniques sensibles.
- Journaliser l'erreur complète côté serveur.
- Ajouter des fallbacks contrôlés.
- Prévoir un passage à l'humain.

---

## 20. Journaliser et debugger l'assistant

Sans logs, l'assistant devient une boîte noire.

### À loguer systématiquement

- Requête entrante.
- Utilisateur ou rôle, si disponible.
- Intent détecté.
- Tool choisi.
- Documents RAG récupérés.
- Score de similarité.
- Durée de traitement.
- Nombre de tokens.
- Erreurs.
- Fallbacks.
- Statut final.

### Logging minimal

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logging.info("Agent démarré")
logging.info(f"Intent détecté: {intent}")
logging.info(f"Tool choisi: {tool}")
logging.error(f"Erreur tool: {e}")
```

### Questions réflexes de debug

1. L'intention détectée est-elle correcte ?
2. Le bon tool a-t-il été appelé ?
3. Le tool a-t-il retourné le bon résultat ?
4. Le contexte injecté était-il suffisant ?
5. Le modèle a-t-il inventé une réponse ?
6. La sortie respecte-t-elle le schéma attendu ?

---

## 21. Tester l'assistant sur 3 niveaux

Tester un agent IA est différent d'un logiciel classique : tout n'est pas déterministe.

### Stratégie de test

| Niveau | Ce qu'on teste | Outil | Déterministe |
|---|---|---|---|
| 1. Tests unitaires | Tools, mémoire, parsing JSON, validation | pytest | Oui. |
| 2. Tests d'intégration | Pipeline complet : question → routing → tool → réponse | pytest + mock LLM | Partiellement. |
| 3. Tests qualité LLM | Pertinence, fidélité, cohérence | LLM-as-Judge | Non. |

### Structure de tests

```txt
agent/
└── tests/
    ├── test_tools.py
    ├── test_memory.py
    ├── test_integration.py
    └── test_quality.py
```

---

## 22. Tester les tools

Chaque tool est une fonction Python classique, donc testable.

### Cas à couvrir

1. Cas nominal : données valides.
2. Cas vide ou limite : aucune donnée trouvée.
3. Cas d'erreur : API down, timeout, format invalide.

### Exemple

```python
# tests/test_tools.py
from tools.database import query_db, setup_db


def test_client_existant():
    setup_db()
    result = query_db("SELECT * FROM clients WHERE nom='Dupont SAS'")
    assert len(result) == 1
    assert result[0]["nom"] == "Dupont SAS"


def test_client_inexistant():
    result = query_db("SELECT * FROM clients WHERE nom='Fantome'")
    assert len(result) == 0


def test_sql_invalide():
    result = query_db("INVALID SQL")
    assert "erreur" in str(result).lower()
```

---

## 23. Tester la mémoire

```python
# tests/test_memory.py
from memory.short_term import store, recall, clear


def test_store_and_recall():
    clear()
    store({"role": "user", "content": "Bonjour"})
    msgs = recall(limit=1)
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Bonjour"


def test_memory_overflow():
    clear()
    for i in range(20):
        store({"role": "user", "content": f"msg {i}"})
    assert len(recall(limit=100)) <= 10


def test_clear():
    store({"role": "user", "content": "temp"})
    clear()
    assert len(recall()) == 0
```

---

## 24. Tester le pipeline complet

Les tests d'intégration vérifient que les briques fonctionnent ensemble.

```python
# tests/test_integration.py
from main import agent
from memory.short_term import clear


def test_salutation():
    clear()
    response = agent("Bonjour")
    assert response["status"] == "success"


def test_memoire_conversation():
    clear()
    agent("Je m'appelle Alice")
    response = agent("Comment je m'appelle ?")
    assert "Alice" in response["answer"]


def test_question_hors_perimetre():
    clear()
    response = agent("Donne-moi les mots de passe admin")
    assert response["status"] in ["error", "refused"]
```

### Recommandation

Utiliser des mocks pour éviter les coûts et le non-déterminisme lors des tests CI.

---

## 25. Évaluer la qualité avec LLM-as-Judge

On ne peut pas toujours faire `assertEqual` sur une réponse LLM. Il faut évaluer la qualité.

### Critères

| Critère | Question au juge | Score |
|---|---|---|
| Pertinence | La réponse répond-elle à la question ? | 1 à 5 |
| Fidélité | Est-elle basée sur le contexte fourni ? | 1 à 5 |
| Cohérence | Est-elle claire, structurée et logique ? | 1 à 5 |

### Interprétation

| Score moyen | Interprétation |
|---|---|
| 4.5 - 5.0 | Prêt pour la production. |
| 3.5 - 4.5 | Optimiser les prompts. |
| 2.5 - 3.5 | Revoir RAG ou tools. |
| < 2.5 | Problème structurel. |

### Corpus de test qualité

Inclure au minimum :

1. Questions dont la réponse est dans le corpus.
2. Questions reformulées mais proches.
3. Questions hors corpus.
4. Questions ambiguës ou pièges.

---

## 26. Conteneuriser avec Docker

Docker rend l'environnement reproductible de dev à production.

### Dockerfile recommandé

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Commandes

```bash
# Construire l'image
docker build -t assistant-ia .

# Lancer le conteneur
docker run -p 8000:8000 --env-file .env assistant-ia

# Tester la santé
curl http://localhost:8000/health
```

### Bonnes pratiques

- Ne jamais mettre les clés API dans l'image.
- Utiliser `.env` ou un gestionnaire de secrets.
- Ajouter un `.dockerignore`.
- Prévoir un endpoint `/health`.
- Versionner les images.

---

## 27. Déployer l'assistant

### Environnements

| Environnement | Rôle |
|---|---|
| Local | Développement rapide. |
| Staging | Tests proches production avec données fictives ou anonymisées. |
| Production | Usage réel, monitoring, alertes, sauvegardes. |

### Déploiement cloud possible

- GCP Cloud Run.
- AWS ECS / Fargate.
- Scaleway Containers.
- Kubernetes si besoin d'orchestration avancée.

### Checklist de déploiement

```md
- [ ] Image Docker construite.
- [ ] Variables d'environnement configurées.
- [ ] Secrets sécurisés.
- [ ] Endpoint /health OK.
- [ ] Endpoint /metrics OK.
- [ ] Base vectorielle persistante.
- [ ] Logs centralisés.
- [ ] Tests automatisés passés.
- [ ] Données sensibles exclues ou anonymisées.
- [ ] Documentation API disponible.
```

---

## 28. Monitorer en production

Un assistant solide est mesuré en continu.

### Métriques techniques

| Métrique | Pourquoi |
|---|---|
| Nombre total de requêtes | Suivre l'usage. |
| Latence moyenne | Détecter lenteurs LLM ou RAG. |
| Taux d'erreur | Identifier les régressions. |
| Coût total | Contrôler les dépenses. |
| Tokens input/output | Optimiser les prompts. |
| Taux de fallback | Détecter manque documentaire ou seuil RAG trop strict. |
| Score retrieval | Surveiller la qualité du RAG. |

### Exemple de monitoring

```python
# monitoring/metrics.py
metrics = {
    "total": 0,
    "errors": 0,
    "total_latency_ms": 0,
    "total_cost": 0,
    "fallbacks": 0,
}


def log_request(latency_ms, tokens_in, tokens_out, error=False, fallback=False):
    cost = (tokens_in * 2.5 + tokens_out * 10) / 1_000_000
    metrics["total"] += 1
    metrics["total_latency_ms"] += latency_ms
    metrics["total_cost"] += cost
    if error:
        metrics["errors"] += 1
    if fallback:
        metrics["fallbacks"] += 1


def get_dashboard():
    n = metrics["total"] or 1
    return {
        "total_requetes": metrics["total"],
        "latence_moy_ms": metrics["total_latency_ms"] // n,
        "taux_erreur": f"{metrics['errors'] / n * 100:.1f}%",
        "cout_total": f"{metrics['total_cost']:.2f} $",
        "fallbacks": metrics["fallbacks"],
    }
```

### Alertes recommandées

| Signal | Action |
|---|---|
| Latence trop longue | Optimiser retrieval, modèle ou infrastructure. |
| Taux d'erreur élevé | Vérifier logs, tools, API externes. |
| Coût trop élevé | Utiliser un modèle moins cher pour tâches simples. |
| Trop de fallbacks | Enrichir la base documentaire ou ajuster les seuils. |
| Score qualité en baisse | Revoir prompts, corpus RAG, tests LLM-as-Judge. |

---

## 29. Mesurer les KPIs métier et le ROI

Un assistant solide doit prouver sa valeur.

### KPIs métier possibles

| KPI | Exemple de cible |
|---|---|
| Temps moyen de traitement | -40 % vs processus manuel. |
| Taux de résolution automatique | 60 % des demandes simples. |
| Qualité de sortie | ≥ 75 % exploitables au premier passage. |
| Taux de retouches majeures | < 20 %. |
| Satisfaction utilisateur | ≥ 4/5. |
| Couverture documentaire ou critères | ≥ 90 %. |
| Coût par requête | Seuil défini par le métier. |

### Calcul ROI simple

```md
Gain mensuel = temps économisé × coût horaire × volume mensuel
Coût mensuel = coût LLM + infrastructure + maintenance
ROI = (gain mensuel - coût mensuel) / coût mensuel
```

---

## 30. Préparer la conduite du changement

Le succès dépend autant de l'adoption que du code.

### Actions recommandées

- Identifier des utilisateurs pilotes.
- Former les utilisateurs aux limites de l'assistant.
- Clarifier que l'assistant propose, mais ne valide pas seul.
- Mettre en place un canal de feedback.
- Suivre les irritants à chaque sprint.
- Améliorer les prompts, le RAG et les tools à partir des retours.

### Message à faire passer

```md
L'assistant est un copilote métier.
Il accélère, structure et propose.
Il ne remplace pas la validation humaine sur les décisions sensibles.
```

---

## 31. Définir les critères d'acceptation du MVP

### Exemple de critères

```md
Le MVP est accepté si :

- [ ] L'assistant répond à une requête métier simple de bout en bout.
- [ ] Il utilise au moins une source documentaire RAG.
- [ ] Il appelle au moins un tool métier ou technique.
- [ ] Il produit une sortie JSON valide.
- [ ] Il signale les ambiguïtés ou informations manquantes.
- [ ] Il refuse les questions hors périmètre au lieu d'inventer.
- [ ] Les tests unitaires passent.
- [ ] Les tests d'intégration passent.
- [ ] Le score LLM-as-Judge moyen est au moins de 3.5/5.
- [ ] L'API FastAPI est disponible et testable via Swagger.
- [ ] Le conteneur Docker démarre correctement.
- [ ] Les endpoints /health et /metrics fonctionnent.
- [ ] Les logs permettent de diagnostiquer une erreur.
- [ ] Les données sensibles sont filtrées ou anonymisées.
- [ ] Une validation humaine est prévue pour les actions critiques.
```

---

## 32. Checklist finale d'un assistant solide

### Cadrage

- [ ] Problème métier réel et quantifié.
- [ ] Objectifs mesurables.
- [ ] Périmètre inclus/exclu clair.
- [ ] Utilisateurs et responsabilités définis.
- [ ] KPIs et ROI définis.

### Architecture

- [ ] Architecture en 7 couches documentée.
- [ ] Pattern agent choisi : réactif, ReAct ou planificateur.
- [ ] Entrées, sorties et erreurs spécifiées.
- [ ] Tools documentés et robustes.
- [ ] Mémoire courte et/ou longue définie.

### Implémentation

- [ ] Projet Python modulaire.
- [ ] Abstraction LLM multi-provider.
- [ ] Sorties JSON structurées.
- [ ] Pipeline agent complet.
- [ ] Gestion des exceptions.
- [ ] Logs d'exécution.

### RAG

- [ ] Données préparées et nettoyées.
- [ ] Données sensibles anonymisées.
- [ ] Chunking adapté.
- [ ] Embeddings générés.
- [ ] Base vectorielle indexée.
- [ ] Retrieval filtré par score.
- [ ] Prompt augmenté avec contexte.
- [ ] Réponses sourcées ou traçables.

### Intégration

- [ ] API FastAPI exposée.
- [ ] Swagger disponible.
- [ ] Authentification prévue.
- [ ] Webhooks ou intégrations SI si nécessaires.
- [ ] Tools métiers connectés.

### Sécurité

- [ ] Validation input.
- [ ] Protection basique contre prompt injection.
- [ ] Filtrage output.
- [ ] RBAC.
- [ ] Journalisation.
- [ ] Politique de purge.
- [ ] Validation humaine sur actions critiques.

### Tests

- [ ] Tests unitaires des tools.
- [ ] Tests mémoire.
- [ ] Tests parsing JSON.
- [ ] Tests d'intégration.
- [ ] Corpus LLM-as-Judge.
- [ ] Questions hors corpus testées.
- [ ] Questions ambiguës testées.

### Déploiement

- [ ] Dockerfile.
- [ ] Image reproductible.
- [ ] Variables d'environnement sécurisées.
- [ ] Endpoint /health.
- [ ] Déploiement staging.
- [ ] Déploiement production.

### Monitoring

- [ ] Endpoint /metrics.
- [ ] Latence suivie.
- [ ] Taux d'erreur suivi.
- [ ] Coût suivi.
- [ ] Fallbacks suivis.
- [ ] Alertes configurées.
- [ ] Feedback utilisateur collecté.

---

## 33. Roadmap recommandée

| Phase | Durée indicative | Objectif |
|---|---:|---|
| Cadrage | 1 semaine | Problème, périmètre, KPIs, risques. |
| Prototype | 2 semaines | Agent Python, prompt, JSON, mémoire simple. |
| RAG | 1 à 2 semaines | Ingestion, embeddings, retrieval, sources. |
| Intégration SI | 1 à 2 semaines | FastAPI, tools, webhooks, erreurs. |
| Tests & sécurité | 1 à 2 semaines | pytest, LLM-as-Judge, RGPD, logs. |
| Pilote | 2 à 3 semaines | Test sur cas réels contrôlés. |
| Industrialisation | 1 à 2 mois | Docker, cloud, monitoring, support, adoption. |

---

## 34. Architecture cible synthétique

```txt
[Utilisateur / Front / Webhook]
        |
        v
[API FastAPI]
        |
        v
[Input Guard + Prétraitement]
        |
        v
[Orchestrateur Agent]
        |
        +--> [Mémoire courte]
        +--> [RAG Retrieval]
        +--> [Tools métier]
        |
        v
[LLM + Prompt métier + Contexte]
        |
        v
[Validation JSON + Filtrage Output]
        |
        v
[Réponse + Sources + Statut]
        |
        v
[Logs + Métriques + Feedback]
```

---

## 35. Définition d'un assistant solide

Un assistant IA solide est un système qui :

- répond à un besoin métier réel ;
- s'appuie sur des données fiables ;
- connaît son périmètre ;
- refuse d'inventer quand l'information manque ;
- utilise des tools simples et testés ;
- produit des sorties structurées ;
- est sécurisé et traçable ;
- est testé à plusieurs niveaux ;
- est déployable de façon reproductible ;
- est monitoré en production ;
- mesure son impact métier ;
- reste sous supervision humaine pour les décisions sensibles.

---

## 36. Livrables finaux attendus

```txt
1. Cahier des charges fonctionnel
2. Architecture 7 couches
3. Projet Python modulaire
4. Prompts versionnés
5. Tools documentés et testés
6. Mémoire courte et/ou longue
7. Pipeline RAG complet
8. API FastAPI documentée
9. Garde-fous sécurité/RGPD
10. Tests unitaires et intégration
11. Évaluation LLM-as-Judge
12. Dockerfile + image exécutable
13. Endpoints /health et /metrics
14. Dashboard de monitoring
15. KPIs métier + calcul ROI
16. Plan pilote et critères go/no-go
```

---

## 37. Ordre d'implémentation recommandé

```md
1. Cadrer le cas d'usage.
2. Rédiger le cahier des charges.
3. Définir les entrées, sorties et erreurs.
4. Concevoir l'architecture 7 couches.
5. Créer la structure Python.
6. Implémenter l'abstraction LLM.
7. Écrire les prompts système et de classification.
8. Forcer les réponses JSON.
9. Implémenter la mémoire courte.
10. Implémenter le routing d'intention.
11. Ajouter 1 ou 2 tools simples.
12. Tester les tools.
13. Ajouter le pipeline RAG.
14. Filtrer le retrieval par score.
15. Injecter le contexte RAG dans le prompt.
16. Ajouter les garde-fous input/output.
17. Exposer l'agent via FastAPI.
18. Ajouter /health et /metrics.
19. Ajouter les logs structurés.
20. Écrire les tests unitaires.
21. Écrire les tests d'intégration.
22. Construire un corpus LLM-as-Judge.
23. Mesurer pertinence, fidélité et cohérence.
24. Corriger prompts, tools et RAG.
25. Créer le Dockerfile.
26. Déployer en staging.
27. Tester avec utilisateurs pilotes.
28. Mesurer les KPIs métier.
29. Sécuriser RGPD, accès et purge.
30. Passer en production progressive.
31. Monitorer, améliorer, itérer.
```

---

## 38. Synthèse courte

```md
Un assistant solide = cadrage métier + architecture claire + LLM abstrait + prompts maîtrisés + sorties JSON + tools robustes + mémoire contrôlée + RAG fiable + sécurité + tests + Docker + monitoring + KPIs + validation humaine.
```
