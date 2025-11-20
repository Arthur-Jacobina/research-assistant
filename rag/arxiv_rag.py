import re
import hashlib
from typing import Dict, Any, List, Optional

from .qdrant import QdrantVectorStore
from .utils import chunk_paper


class ArxivRAG:
    """RAG system specifically designed for ArXiv papers."""
    
    def __init__(self, vector_store: QdrantVectorStore):
        """
        Initialize ArxivRAG with a vector store.
        """
        self.vector_store = vector_store
    
    def _generate_collection_name(self, paper_url: str) -> str:
        """
        Generate a collection name from an ArXiv paper URL.
        """
        arxiv_match = re.search(r'arxiv\.org/(?:abs|html|pdf)/(\d+\.\d+)', paper_url)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1).replace('.', '_')
            collection_name = f"paper_arxiv_{arxiv_id}"
        else:
            url_hash = hashlib.md5(paper_url.encode()).hexdigest()[:8]
            collection_name = f"paper_{url_hash}"
        
        return collection_name
    
    def upload_paper(
        self,
        paper_url: str,
        markdown_text: str,
        min_chunk_size: int = 200,
        max_chunk_size: int = 1500,
        target_chunk_size: int = 1000,
    ) -> Dict[str, Any]:
        """
        Upload an ArXiv paper to the vector store.
        """
        collection_name = self._generate_collection_name(paper_url)
        
        chunks = chunk_paper(
            markdown_text,
            min_chunk_size=min_chunk_size,
            max_chunk_size=max_chunk_size,
            target_chunk_size=target_chunk_size
        )
        
        result = self.vector_store.upload_documents(
            collection_name=collection_name,
            chunks=chunks,
            source_identifier=paper_url,
            recreate_if_exists=False
        )
        
        result["paper_url"] = paper_url
        return result
    
    def search_paper(
        self,
        paper_url: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search within a specific ArXiv paper.
        """
        collection_name = self._generate_collection_name(paper_url)
        return self.vector_store.search(collection_name, query, limit)
    
    def delete_paper(self, paper_url: str) -> bool:
        """
        Delete an ArXiv paper from the vector store.
        """
        collection_name = self._generate_collection_name(paper_url)
        return self.vector_store.delete_collection(collection_name)
    
    def has_paper(self, paper_url: str) -> bool:
        """
        Check if a paper exists in the vector store.
        """
        collection_name = self._generate_collection_name(paper_url)
        return self.vector_store.has_collection(collection_name)
    
    def get_all_papers(self) -> List[str]:
        """
        Get list of all paper collection names.
        """
        all_collections = self.vector_store.get_collections()
        return [col for col in all_collections if col.startswith('paper_')]

