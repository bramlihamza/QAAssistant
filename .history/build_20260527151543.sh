#!/bin/bash
set -e

echo "🔍 Current directory: $(pwd)"
echo "📂 Listing root files:"
ls -la

echo ""
echo "📦 Building Nuxt frontend..."

# Vérifier que le dossier frontend existe
if [ ! -d "frontend" ]; then
  echo "❌ Frontend directory not found!"
  exit 1
fi

# Installer et build
cd frontend
npm install
npm run build

echo "✅ Build complete!"

