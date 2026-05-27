"""
Adaptateur vectorisation multi-backend.
Utilise ChromaDB en développement, Pinecone en production (Vercel).
"""

import os
from typing import List, Dict, Any

_BACKEND = os.getenv("RAG_BACKEND", "pinecone" if os.getenv("VERCEL") else "chromadb")


class VectorStore:
    """Interface unifiée pour ChromaDB et Pinecone."""
    
    def __init__(self):
        self.backend = _BACKEND
        
        if self.backend == "pinecone":
            self._init_pinecone()
        else:
            self._init_chromadb()
    
    def _init_chromadb(self):
        """Initialise ChromaDB (mode développement)."""
        try:
            import chromadb
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name="istqb",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ ChromaDB initialisé")
        except Exception as e:
            print(f"❌ Erreur ChromaDB: {e}")
            self.client = None
    
    def _init_pinecone(self):
        """Initialise Pinecone (mode production Vercel)."""
        try:
            from pinecone import Pinecone
            
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX", "qa-assistant")
            
            if not api_key:
                raise ValueError("PINECONE_API_KEY not set")
            
            pc = Pinecone(api_key=api_key)
            self.index = pc.Index(index_name)
            print(f"✅ Pinecone initialisé (index: {index_name})")
        except Exception as e:
            print(f"❌ Erreur Pinecone: {e}")
            self.index = None
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Recherche dans la base vectorielle."""
        
        if self.backend == "pinecone" and self.index:
            try:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                return [
                    {
                        "id": match["id"],
                        "score": match["score"],
                        "text": match.get("metadata", {}).get("text", ""),
                    }
                    for match in results.get("matches", [])
                ]
            except Exception as e:
                print(f"❌ Erreur Pinecone search: {e}")
                return []
        
        elif self.backend == "chromadb" and self.collection:
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    include=["documents", "distances", "metadatas"]
                )
                
                if results["ids"] and results["ids"][0]:
                    return [
                        {
                            "id": results["ids"][0][i],
                            "score": 1 - results["distances"][0][i],  # Convertir distance en similarité
                            "text": results["documents"][0][i],
                        }
                        for i in range(len(results["ids"][0]))
                    ]
            except Exception as e:
                print(f"❌ Erreur ChromaDB search: {e}")
        
        return []


# Instance globale
vector_store = VectorStore()
