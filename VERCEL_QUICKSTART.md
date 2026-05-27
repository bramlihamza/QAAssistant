# Déploiement Vercel — Guide rapide

## ⚡ 5 étapes

### 1️⃣ Préparer Pinecone (5 min)
```
A. https://www.pinecone.io → "Get started free"
B. Créez un index "qa-assistant" (1536 dimensions, cosine)
C. Récupérez API Key et Environment
```

### 2️⃣ Préparer OpenAI (2 min)
```
A. https://platform.openai.com/api-keys → Create key
B. Copiez la clé (ex: sk-proj-xxxx)
```

### 3️⃣ Indexer les PDFs localement (5 min)
```bash
cd agent
pip install -r requirements.txt
cp .env.example .env
# Éditez .env avec les clés

python scripts/ingest_docs_pinecone.py
# Résultat: ✅ 341 chunks indexés
```

### 4️⃣ Déployer sur Vercel (5 min)
```bash
# Commit et push
git add .
git commit -m "Prêt pour Vercel"
git push origin main

# Vercel: https://vercel.com/new
# 1. Import repo GitHub
# 2. Add variables d'env (OPENAI_API_KEY, PINECONE_*)
# 3. Deploy
```

### 5️⃣ Tester (2 min)
```bash
curl https://your-url.vercel.app/api/health
```

## 📚 Documentation complète

Voir [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🔧 Architecture

```
Vercel
├── Frontend (Nuxt)     → /
├── API Python          → /api/*
│   ├── /api/ask        POST
│   ├── /api/health     GET
│   ├── /api/metrics    GET
│   └── /api/user-stories GET
└── Pinecone (vectorDB) ← Externe
```

## 💰 Coûts

- **Vercel** : Gratuit (100 GB/mois)
- **OpenAI** : ~$0.002/requête (gratuit: $5 starter)
- **Pinecone** : Gratuit (100k vectors)
- **Total** : $0–50/mois

## 🆘 Problèmes courants

| Erreur | Solution |
|---|---|
| `OPENAI_API_KEY not set` | Vérifiez variables d'env Vercel |
| `Timeout 30s` | Augmentez `maxDuration` dans `vercel.json` |
| `Chunks non indexés` | Exécutez `python scripts/ingest_docs_pinecone.py` |

## 📖 Ressources

- [DEPLOYMENT.md](./DEPLOYMENT.md) — Guide détaillé
- [README.md](./README.md) — Documentation complète
- Vercel Docs: https://vercel.com/docs
- Pinecone Docs: https://docs.pinecone.io
