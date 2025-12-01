import re

from typing import Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

from rag.utils import Chunk


load_dotenv()


class QdrantVectorStore:
    """Vector store for documents in Qdrant."""

    def __init__(self, url: str = 'http://localhost:6333', model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.client = QdrantClient(url=url)
        self.embedding_model_name = model_name

    def _sanitize_collection_name(self, collection_name: str) -> str:
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', collection_name)
        if sanitized and sanitized[0].isdigit():
            sanitized = f'col_{sanitized}'
        return sanitized if sanitized else 'collection'

    def upload_documents(
        self,
        collection_name: str,
        chunks: list[Chunk],
        source_identifier: str | None = None,
        recreate_if_exists: bool = True,
    ) -> dict[str, Any]:
        """Upload documents to a Qdrant collection."""
        collection_name = self._sanitize_collection_name(collection_name)

        docs = []
        payload = []
        ids = []

        for idx, chunk in enumerate(chunks):
            docs.append(models.Document(
                text=chunk.page_content,
                model=self.embedding_model_name
            ))

            chunk_payload = {
                'document': chunk.page_content,
                'chunk_id': idx,
                **chunk.metadata
            }

            if source_identifier:
                chunk_payload['source'] = source_identifier

            payload.append(chunk_payload)
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
            if 'already exists' in str(e).lower():
                if recreate_if_exists:
                    self.client.delete_collection(collection_name)
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=self.client.get_embedding_size(self.embedding_model_name),
                            distance=models.Distance.COSINE
                        )
                    )
                else:
                    raise ValueError(f'Collection {collection_name} already exists')
            else:
                raise

        self.client.upload_collection(
            collection_name=collection_name,
            vectors=docs,
            ids=ids,
            payload=payload,
        )

        return {
            'collection_name': collection_name,
            'source': source_identifier,
            'num_chunks': len(chunks),
            'status': 'success'
        }

    def search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5
    ) -> list[dict[str, Any]]:
        """Search within a specific collection."""
        collection_name = self._sanitize_collection_name(collection_name)

        query_doc = models.Document(text=query, model=self.embedding_model_name)

        search_result = self.client.query_points(
            collection_name=collection_name,
            query=query_doc,
            limit=limit
        ).points

        results = []
        for point in search_result:
            result = {
                'id': point.id,
                'score': point.score,
                **point.payload
            }
            results.append(result)

        return results

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        collection_name = self._sanitize_collection_name(collection_name)
        return self.client.delete_collection(collection_name)

    def has_collection(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        collection_name = self._sanitize_collection_name(collection_name)
        return any(collection_name == x.name for x in self.client.get_collections().collections)

    def get_collections(self) -> list[str]:
        """Get list of all collection names."""
        return [x.name for x in self.client.get_collections().collections]
