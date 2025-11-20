import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from rag.qdrant import QdrantVectorStore

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_qdrant_store = QdrantVectorStore(url=qdrant_url, model_name=model_name)

def insert_paper(url: str, markdown: str) -> bool:
    try:
        _qdrant_store.upload_paper(url, markdown)
        return True
    except Exception as e:
        print(f"Error inserting paper: {e}")
        return False

def get_paper(url: str, query: Optional[str] = None, limit: int = 5) -> Optional[Dict[str, Any]]:
    try:
        if not _qdrant_store.has_collection(url):
            return None
        
        if query:
            search_results = _qdrant_store.search_paper(url, query, limit)
            return {
                "url": url,
                "query": query,
                "results": search_results,
                "markdown": "\n\n".join([r["document"] for r in search_results])
            }
        
        return "Paper found. Use a query to get more information."
    except Exception as e:
        print(f"Error getting paper: {e!s}")
        return None
