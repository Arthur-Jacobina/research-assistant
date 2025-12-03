import os

from typing import Any

from dotenv import load_dotenv

from rag.arxiv_rag import ArxivRAG
from rag.qdrant import QdrantVectorStore


load_dotenv()

qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
_vector_store = QdrantVectorStore(url=qdrant_url, model_name=model_name)
_arxiv_rag = ArxivRAG(vector_store=_vector_store)

def insert_paper(url: str, markdown: str) -> bool:
    try:
        _arxiv_rag.upload_paper(url, markdown)
        return True
    except Exception as e:
        print(f'Error inserting paper: {e}')
        return False

def get_paper(url: str, query: str | None = None, limit: int = 5) -> dict[str, Any] | None:
    try:
        if not _arxiv_rag.has_paper(url):
            return None

        if query:
            search_results = _arxiv_rag.search_paper(url, query, limit)
            return {
                'url': url,
                'query': query,
                'results': search_results,
                'markdown': '\n\n'.join([r['document'] for r in search_results])
            }

        return {'markdown': "Paper found. Use a query to get more information. Don't return error messages."}
    except Exception as e:
        print(f'Error getting paper: {e!s}')
        return None
