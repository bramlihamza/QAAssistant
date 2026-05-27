# 🚀 Guide de déploiement sur Vercel

## Prérequis

1. **Compte Vercel** : https://vercel.com
2. **Compte OpenAI** : https://platform.openai.com
3. **Compte Pinecone** : https://pinecone.io
4. **Git + GitHub** : Dépôt public ou privé

## Étape 1 : Préparer Pinecone (base vectorielle)

### 1.1 Créer un compte Pinecone
- Allez sur https://www.pinecone.io
- Cliquez "Get started free"
- Créez un compte (gratuit : 1 index, 100k vectors)

### 1.2 Créer un index
- Dans le dashboard Pinecone, cliquez "Create Index"
- **Nom** : `qa-assistant`
- **Dimensions** : `1536` (pour text-embedding-3-small)
- **Metric** : `cosine`
- Cliquez "Create"

### 1.3 Récupérer les clés
- Dashboard → API Keys
- Copiez :
  - `API Key` (ex: `pcak_xxxxx`)
  - `Environment` (ex: `gcp-starter`)

## Étape 2 : Préparer OpenAI

### 2.1 Créer une clé API
- Allez sur https://platform.openai.com/api-keys
- Cliquez "Create new secret key"
- Copiez la clé (ex: `sk-proj-xxxxx`)

### 2.2 Configurer le projet
- OpenAI → Settings → Billing
- Vérifiez que vous avez du crédit (gratuit : $5)

## Étape 3 : Préparer les PDFs ISTQB (indexation locale)

Avant le premier déploiement, indexez les PDFs dans Pinecone :

```bash
# 1. Cloner le repo
git clone https://github.com/[votre-username]/QAAssistant.git
cd QAAssistant

# 2. Installer dépendances locales
cd agent
pip install -r requirements.txt

# 3. Configurer .env
cp .env.example .env
# Éditez .env avec:
# - OPENAI_API_KEY
# - PINECONE_API_KEY
# - PINECONE_INDEX
# - PINECONE_ENVIRONMENT

# 4. Indexer les PDFs ISTQB
python scripts/ingest_docs.py

# Résultat: "✅ 341 chunks indexés dans Pinecone"
```

## Étape 4 : Déployer sur Vercel

### 4.1 Push vers GitHub
```bash
git add .
git commit -m "Préparation déploiement Vercel"
git push origin main
```

### 4.2 Connecter Vercel
1. Allez sur https://vercel.com/new
2. Cliquez "Import Git Repository"
3. Sélectionnez votre repo `QAAssistant`
4. Cliquez "Import"

### 4.3 Configurer les variables d'environnement
Dans Vercel, allez à **Settings → Environment Variables** et ajoutez :

| Clé | Valeur |
|---|---|
| `OPENAI_API_KEY` | `sk-proj-xxxxx` |
| `PINECONE_API_KEY` | `pcak_xxxxx` |
| `PINECONE_INDEX` | `qa-assistant` |
| `PINECONE_ENVIRONMENT` | `gcp-starter` |
| `MODEL` | `gpt-4o-mini` |
| `TEMPERATURE` | `0` |

### 4.4 Déployer
- Vercel détecte automatiquement :
  - **Frontend Nuxt** (dossier `frontend/`)
  - **API Python** (dossier `api/`)
- Cliquez "Deploy"
- ⏳ Attendre ~3-5 minutes

## Étape 5 : Tester l'API

### 5.1 Health Check
```bash
curl https://your-vercel-url.vercel.app/api/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "checks": {
    "api": "✅ OK",
    "openai_api_key": "✅ Configuré",
    "pinecone_api_key": "✅ Configuré"
  }
}
```

### 5.2 Tester l'endpoint /ask
```bash
curl -X POST https://your-vercel-url.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Générer 3 cas de test pour la user story US-006"
  }'
```

### 5.3 Tester le frontend
Accédez à : https://your-vercel-url.vercel.app

## Dépannage

### ❌ "OPENAI_API_KEY not set"
→ Vérifiez les variables d'env dans Vercel Settings

### ❌ "PINECONE_API_KEY not set"
→ Vérifiez Pinecone_API_KEY dans Vercel Settings

### ❌ "Vercel Function timeout"
- Vérifiez `vercel.json` : `"maxDuration": 30` (30 secondes)
- Si l'API prend >30s, augmentez à 60 ou 300

### ❌ "Chunks non indexés"
- Exécutez `python scripts/ingest_docs.py` localement
- Vérifiez que les chunks sont présents dans Pinecone

## Coûts estimés (gratuit → premium)

| Service | Gratuit | Coût |
|---|---|---|
| **Vercel** | ✅ 100 GB/mois | $20/mois (pro) |
| **OpenAI** | ❌ | ~$0.002/requête |
| **Pinecone** | ✅ 100k vectors | $0.70/M vectors |
| **Total** | - | $10–50/mois |

## URLs utiles

- Vercel Dashboard: https://vercel.com/dashboard
- Pinecone Dashboard: https://app.pinecone.io
- OpenAI API Keys: https://platform.openai.com/api-keys
- QA Assistant Docs: [README.md](./README.md)

## Support

En cas de problème :
1. Consultez les logs Vercel : Dashboard → Deployments → Logs
2. Vérifiez la console navigateur (F12)
3. Ouvrez une issue sur GitHub
