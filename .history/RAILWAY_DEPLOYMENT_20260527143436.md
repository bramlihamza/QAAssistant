# 🚀 Déploiement API sur Railway

## Architecture finale

```
┌─────────────────────────────────────────────────┐
│ Frontend Nuxt (Vercel)                          │
│ https://qa-assistant-three.vercel.app           │
└────────────────┬────────────────────────────────┘
                 │ API calls
                 ↓
┌─────────────────────────────────────────────────┐
│ API Python FastAPI (Railway)                    │
│ https://qa-assistant-api-prod.railway.app       │
└─────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│ Pinecone (Vectorisation ISTQB)                  │
│ https://app.pinecone.io                         │
└─────────────────────────────────────────────────┘
```

---

## ⚡ 5 étapes de déploiement

### **Étape 1 : Préparer Pinecone (5 min)**

Si vous l'avez déjà fait, passez à l'étape 2.

```
1. https://www.pinecone.io → "Get started free"
2. Créez un index "qa-assistant"
   - Dimensions: 1536
   - Metric: cosine
3. Récupérez :
   - API Key (ex: pcak_xxx)
   - Environment (ex: gcp-starter)
```

### **Étape 2 : Indexer les PDFs ISTQB localement (10 min)**

Depuis votre PC local :

```bash
# Aller au dossier agent
cd agent

# Configurer .env
cp .env.example .env

# Éditer .env avec :
# OPENAI_API_KEY=sk-proj-xxx
# PINECONE_API_KEY=pcak-xxx
# PINECONE_INDEX=qa-assistant
# PINECONE_ENVIRONMENT=gcp-starter

# Installer les dépendances
pip install -r requirements.txt

# Indexer les PDFs
python scripts/ingest_docs_pinecone.py

# Résultat: ✅ 341 chunks indexés dans Pinecone
```

### **Étape 3 : Créer un compte Railway (2 min)**

1. Allez sur https://railway.app
2. Cliquez "Start Free"
3. Connectez votre compte GitHub (ou créez un compte)
4. Acceptez les permissions

### **Étape 4 : Déployer sur Railway (5 min)**

#### 4.1 Créer un nouveau projet
```
1. https://railway.app/dashboard
2. Cliquez "New Project" → "Deploy from GitHub"
3. Sélectionnez votre repo "QAAssistant"
4. Railway détecte automatiquement le Dockerfile
```

#### 4.2 Configurer les variables d'env
Dans Railway, allez à **Project → Variables** et ajoutez :

| Variable | Valeur |
|---|---|
| `OPENAI_API_KEY` | `sk-proj-votre-clé` |
| `PINECONE_API_KEY` | `pcak-votre-clé` |
| `PINECONE_INDEX` | `qa-assistant` |
| `PINECONE_ENVIRONMENT` | `gcp-starter` |
| `MODEL` | `gpt-4o-mini` |
| `TEMPERATURE` | `0` |

#### 4.3 Configurer le déploiement
```
1. Dans Railway, allez à "Settings"
2. **Root Directory** : Aucun (défaut)
3. **Dockerfile** : `Dockerfile.railway`
4. **Port** : `8000`
```

#### 4.4 Déployer
```
1. Cliquez "Deploy"
2. Attendez 3-5 minutes
3. Vous recevrez une URL publique (ex: https://qa-assistant-api-prod.railway.app)
```

### **Étape 5 : Configurer Vercel pour pointer vers Railway (2 min)**

1. https://vercel.com/dashboard
2. Allez sur votre projet **qa-assistant-three**
3. **Settings → Environment Variables**
4. Ajoutez/modifiez :

| Variable | Valeur |
|---|---|
| `QA_API_BASE` | `https://qa-assistant-api-prod.railway.app` |

5. Vercel redéploiera automatiquement

---

## ✅ Tester le déploiement

### Health check API
```bash
curl https://qa-assistant-api-prod.railway.app/api/health
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

### Frontend
```
https://qa-assistant-three.vercel.app
```

Vous devez voir l'interface Nuxt avec le chatbox connecté à l'API Railway.

---

## 📊 Coûts (gratuit → premium)

| Service | Gratuit | Coût |
|---|---|---|
| **Railway** | ✅ $5 starter credit | Payant après |
| **Vercel** | ✅ 100 GB/mois | $20+/mois (pro) |
| **OpenAI API** | ❌ | ~$0.002/requête |
| **Pinecone** | ✅ 100k vectors | $0.70/M vectors |
| **Total** | - | $20–50/mois |

---

## 🆘 Dépannage

### Railway : "Build failed"
```
→ Vérifiez les logs : Dashboard → Deployments → Logs
→ Vérifiez requirements.txt existe et est correct
→ Vérifiez Dockerfile.railway pointe vers agent/requirements.txt
```

### Railway : "Port 8000 not exposed"
```
→ Vérifiez EXPOSE 8000 dans Dockerfile.railway
→ Vérifiez PORT=8000 dans les variables d'env
```

### Frontend 404 après changement d'API
```
→ Attendez 1-2 min après modification des variables Vercel
→ Hard refresh : Ctrl+Shift+R (ne pas utiliser le cache)
```

### API retourne 500
```
→ Vérifiez OPENAI_API_KEY dans Railway Variables
→ Vérifiez PINECONE_API_KEY dans Railway Variables
→ Vérifiez les chunks sont indexés dans Pinecone
→ Consultez les logs Railway en temps réel
```

---

## 📚 Ressources

- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [Pinecone Docs](https://docs.pinecone.io)
- [README Principal](./README.md)

---

## 🎯 Résumé des URLs

| Service | URL |
|---|---|
| **Frontend** | https://qa-assistant-three.vercel.app |
| **API** | https://qa-assistant-api-prod.railway.app |
| **API Health** | https://qa-assistant-api-prod.railway.app/api/health |
| **Vercel Dashboard** | https://vercel.com/dashboard |
| **Railway Dashboard** | https://railway.app/dashboard |
| **Pinecone Dashboard** | https://app.pinecone.io |
