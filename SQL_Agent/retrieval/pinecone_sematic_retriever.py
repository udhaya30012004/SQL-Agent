import os
from typing import List, Dict, Any

from pinecone import Pinecone

from SQL_Agent.embeddings.embeddings_client import EmbeddingClient


DEFAULT_INDEX_NAME = "sql-agent"


class PineconeSemanticRetriever:
    def __init__(self,index_name: str = DEFAULT_INDEX_NAME,namespace: str = "default"):
        self.index_name = os.getenv("PINECONE_INDEX_NAME", index_name)
        self.namespace = namespace

        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        self.index = self.pc.Index(self.index_name)
        self.embedding_client = EmbeddingClient()

    def search(self,question: str,top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_client.embed_query(question)

        response = self.index.query(
              vector=query_embedding,
              top_k=top_k,
              namespace=self.namespace,
              include_metadata=True
        )

        candidates = []

        for match in response.get("matches", []):
            metadata = match.get("metadata", {})
            table_name = metadata.get("table_name") or match.get("id")
            score = float(match.get("score", 0.0))

            candidates.append({
                  "table": table_name,
                  "score": score,
                  "source": "semantic"
              })

        return candidates