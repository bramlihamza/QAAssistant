#!/bin/bash
# Script de build pour Vercel
# Installe et build le frontend Nuxt

set -e

echo "📦 Building Nuxt frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
