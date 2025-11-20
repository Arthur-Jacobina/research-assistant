from qdrant_client import QdrantClient, models
from typing import List, Dict, Any, Optional
import hashlib
import re
import os
from dotenv import load_dotenv

from .utils import chunk_paper, Chunk

load_dotenv()


class QdrantVectorStore:
    """Store and search research papers in Qdrant."""
    
    def __init__(self, url: str = "http://localhost:6333", model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.client = QdrantClient(url=url)
        self.embedding_model_name = model_name
    
    def _sanitize_collection_name(self, paper_url: str) -> str:
        url_hash = hashlib.md5(paper_url.encode()).hexdigest()[:8]
        
        arxiv_match = re.search(r'arxiv\.org/(?:abs|html)/(\d+\.\d+)', paper_url)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1).replace('.', '_')
            return f"paper_arxiv_{arxiv_id}"
        
        return f"paper_{url_hash}"
    
    def upload_paper(
        self,
        paper_url: str,
        markdown_text: str,
        min_chunk_size: int = 200,
        max_chunk_size: int = 1500,
        target_chunk_size: int = 1000,
    ) -> Dict[str, Any]:
        collection_name = self._sanitize_collection_name(paper_url)
        
        chunks = chunk_paper(
            markdown_text,
            min_chunk_size=min_chunk_size,
            max_chunk_size=max_chunk_size,
            target_chunk_size=target_chunk_size
        )
        
        docs = []
        payload = []
        ids = []
        
        for idx, chunk in enumerate(chunks):
            docs.append(models.Document(
                text=chunk.page_content,
                model=self.model_name
            ))
            
            payload.append({
                "document": chunk.page_content,
                "source": paper_url,
                "chunk_id": idx,
                "title": chunk.metadata.get("title"),
                "section": chunk.metadata.get("section"),
                "subsection": chunk.metadata.get("subsection"),
            })
            
            ids.append(idx)
        
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.client.get_embedding_size(self.embedding_model_name),
                    distance=models.Distance.COSINE
                )
            )
        except Exception as e:
            if "already exists" in str(e).lower():
                self.client.delete_collection(collection_name)
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=self.client.get_embedding_size(self.embedding_model_name),
                        distance=models.Distance.COSINE
                    )
                )
            else:
                raise
        
        self.client.upload_collection(
            collection_name=collection_name,
            vectors=docs,
            ids=ids,
            payload=payload,
        )
        
        return {
            "collection_name": collection_name,
            "paper_url": paper_url,
            "num_chunks": len(chunks),
            "status": "success"
        }
    
    def search_paper(
        self,
        paper_url: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search within a specific paper."""
        collection_name = self._sanitize_collection_name(paper_url)
        
        query_doc = models.Document(text=query, model=self.embedding_model_name)
        
        search_result = self.client.query_points(
            collection_name=collection_name,
            query=query_doc,
            limit=limit
        ).points
        
        results = []
        for point in search_result:
            results.append({
                "id": point.id,
                "score": point.score,
                "document": point.payload.get("document"),
                "source": point.payload.get("source"),
                "title": point.payload.get("title"),
                "section": point.payload.get("section"),
                "subsection": point.payload.get("subsection"),
            })
        
        return results
    
    def delete_paper(self, paper_url: str) -> bool:
        """Delete a paper collection."""
        collection_name = self._sanitize_collection_name(paper_url)
        return self.client.delete_collection(collection_name)

    def has_collection(self, paper_url: str) -> bool:
        collection_name = self._sanitize_collection_name(paper_url)
        return any(collection_name == x.name for x in self.client.get_collections().collections)