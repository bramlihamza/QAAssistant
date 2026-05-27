# 🚀 Déploiement complet QA Assistant

## Architecture
- **Frontend** : Nuxt.js → Vercel
- **API** : FastAPI + Python → Railway  
- **Vectorisation** : Pinecone

---

## ⚡ Déploiement rapide (15 min)

### Phase 1 : Indexer les PDFs (local, une fois)
```bash
cd agent
pip install -r requirements.txt
cp .env.example .env
# Éditez .env avec vos clés Pinecone + OpenAI

python scripts/ingest_docs_pinecone.py
# Résultat: ✅ 341 chunks indexés
```

### Phase 2 : Déployer l'API sur Railway (5 min)
```
1. https://railway.app/new
2. Import GitHub repo
3. Root Directory: (empty)
4. Dockerfile: Dockerfile.railway
5. Variables d'env:
   - OPENAI_API_KEY
   - PINECONE_API_KEY
   - PINECONE_INDEX
   - PINECONE_ENVIRONMENT
6. Deploy
7. Notez l'URL (ex: https://qa-assistant-api-prod.railway.app)
```

### Phase 3 : Déployer le Frontend sur Vercel (5 min)
```
1. https://vercel.com/new
2. Import GitHub repo
3. Framework: Auto-detect (Nuxt)
4. Environment Variables:
   - QA_API_BASE = https://votre-railway-url.railway.app
   - PUBLIC_API_BASE = https://votre-railway-url.railway.app
5. Deploy
6. Notez l'URL (ex: https://qa-assistant-three.vercel.app)
```

---

## ✅ Tester

### 1. API Health
```bash
curl https://YOUR_RAILWAY_URL/api/health
# {"status": "healthy", "checks": {...}}
```

### 2. Frontend
```
https://YOUR_VERCEL_URL
```

---

## 📖 Documentation complète

- **API Railway** → [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- **Architecture** → [README.md](./README.md)
- **Guide Vercel** → [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 🔑 Clés requises

Avant de commencer, vous devez avoir :

1. **OpenAI API Key** → https://platform.openai.com/api-keys
2. **Pinecone API Key** → https://pinecone.io
3. **GitHub Account** → Repo public
4. **Railway Account** → https://railway.app
5. **Vercel Account** → https://vercel.app
