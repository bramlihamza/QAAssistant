# 🚀 Déploiement complet sur Vercel

## Architecture
```
┌──────────────────────────────────────┐
│ Vercel                               │
├──────────────────────────────────────┤
│ Frontend Nuxt (/                     │
├──────────────────────────────────────┤
│ API Python Serverless (/api/*)       │
├──────────────────────────────────────┤
│ Pinecone (Vectorisation ISTQB)       │
└──────────────────────────────────────┘
```

---

## ⚡ Procédure (25 min)

### Étape 1 : Indexer les PDFs localement (10 min)

```bash
cd agent
pip install -r requirements.txt

# Configurer .env
cp .env.example .env

# Éditer .env avec :
# OPENAI_API_KEY=sk-proj-votre-clé
# PINECONE_API_KEY=pcak-votre-clé
# PINECONE_INDEX=qa-assistant
# PINECONE_ENVIRONMENT=gcp-starter

# Indexer
python scripts/ingest_docs_pinecone.py

# Résultat: ✅ 341 chunks indexés dans Pinecone
```

### Étape 2 : Committer et pusher (2 min)

```bash
git add .
git commit -m "🚀 Deploy everything on Vercel"
git push origin main
```

### Étape 3 : Configurer Vercel (5 min)

1. Allez à https://vercel.com/dashboard
2. Cliquez sur le projet **qa-assistant-three**
3. **Settings → Environment Variables**
4. Ajoutez ces variables :

| Variable | Valeur |
|---|---|
| `OPENAI_API_KEY` | `sk-proj-votre-clé` |
| `PINECONE_API_KEY` | `pcak-votre-clé` |
| `PINECONE_INDEX` | `qa-assistant` |
| `PINECONE_ENVIRONMENT` | `gcp-starter` |
| `MODEL` | `gpt-4o-mini` |
| `TEMPERATURE` | `0` |

5. Cliquez **Save**
6. Attendez le redéploiement automatique (~2 min)

### Étape 4 : Tester (2 min)

#### A. Health check API
```bash
curl https://qa-assistant-three.vercel.app/api/health
```

Résultat attendu :
```json
{
  "status": "healthy",
  "checks": {
    "api": "✅ OK",
    "openai_api_key": "✅ Configured",
    "pinecone_api_key": "✅ Configured"
  }
}
```

#### B. Frontend
```
https://qa-assistant-three.vercel.app
```

Vous devez voir l'interface Nuxt avec tous les contrôles actifs.

---

## 📋 Endpoints disponibles

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/health` | GET | État de santé |
| `/api/ask` | POST | Générer des cas de test |
| `/api/metrics` | GET | Statistiques |
| `/api/user-stories` | GET | Liste des US |

### Exemple d'appel
```bash
curl -X POST https://qa-assistant-three.vercel.app/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Générer 3 cas de test pour US-006"}'
```

---

## ⚠️ Important : Prérequis Pinecone

L'API ne fonctionnera que si :
1. ✅ Les PDFs ISTQB sont indexés dans Pinecone (Étape 1)
2. ✅ Variables d'env configurées dans Vercel (Étape 3)
3. ✅ Clés API valides (OpenAI + Pinecone)

---

## 🔍 Dépannage

### ❌ `/api/health` retourne 404
```
→ Attendez 2-3 min après commit
→ Vercel détecte les Vercel Functions dans api/
→ Si persiste, vérifiez vercel.json existe
```

### ❌ "OPENAI_API_KEY not configured"
```
→ Allez à Vercel Settings → Environment Variables
→ Vérifiez OPENAI_API_KEY est bien défini
→ Redéployez (Deployments → Redeploy)
```

### ❌ "PINECONE_API_KEY not configured"
```
→ Même procédure pour PINECONE_API_KEY
→ Vérifiez que l'index Pinecone existe
```

### ❌ API timeout (>30 secondes)
```
→ Vercel Functions a un timeout de 30s
→ L'agent QA peut prendre 15s, ce qui est normal
→ Si > 30s, optim nécessaire ou augmenter maxDuration
```

### ❌ "Chunks non indexés"
```
→ Réexécutez localement : python scripts/ingest_docs_pinecone.py
→ Vérifiez dans Pinecone Dashboard que l'index a des vectors
```

---

## 💰 Coûts

| Service | Gratuit | Prix |
|---|---|---|
| **Vercel** | ✅ 100 GB/mois | $20+/mois (pro) |
| **OpenAI API** | ❌ | ~$0.002/requête |
| **Pinecone** | ✅ 100k vectors | $0.70/M vectors |
| **Total** | - | $20–50/mois |

---

## 📚 Architecture détaillée

### Frontend (Nuxt)
- Framework: Nuxt 4
- Build: `npm run build`
- Output: `frontend/.output/public`

### API (Vercel Functions)
- Runtime: Python 3.11
- Endpoints: `api/*.py`
- Handler: fonction `handler(request)`
- Timeout: 30 secondes

### Vectorisation (Pinecone)
- Index: `qa-assistant`
- Dimensions: 1536
- Metric: cosine
- Chunks: 341 (ISTQB documents)

---

## 🔐 Variables d'env requises

```
OPENAI_API_KEY          # Clé API OpenAI (sk-proj-...)
PINECONE_API_KEY        # Clé API Pinecone (pcak-...)
PINECONE_INDEX          # Nom index (qa-assistant)
PINECONE_ENVIRONMENT    # Région (gcp-starter)
MODEL                   # Modèle LLM (gpt-4o-mini)
TEMPERATURE             # Température (0)
```

---

## 📖 Ressources

- **Vercel Docs**: https://vercel.com/docs
- **Pinecone Docs**: https://docs.pinecone.io
- **OpenAI API**: https://platform.openai.com/docs
- **README Principal**: [README.md](./README.md)
