
import os
from typing import Dict, Any

from pinecone import Pinecone, ServerlessSpec

from SQL_Agent.embeddings.embeddings_client import EmbeddingClient


DEFAULT_INDEX_NAME = "sql-agent"
DEFAULT_DIMENSION = 768
DEFAULT_METRIC = "cosine"


class PineconeSchemaIndex:
    def __init__(
          self,
          index_name: str = DEFAULT_INDEX_NAME,
          dimension: int = DEFAULT_DIMENSION,
          metric: str = DEFAULT_METRIC
      ):
        self.index_name = os.getenv("PINECONE_INDEX_NAME", index_name)
        self.dimension = dimension
        self.metric = metric

        self.pc = Pinecone(
              api_key=os.getenv("PINECONE_API_KEY")
          )

        self.embedding_client = EmbeddingClient(
              output_dimension=self.dimension
          )

        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self) -> None:
        existing_indexes = [
              index_info["name"]
              for index_info in self.pc.list_indexes()
          ]

        if self.index_name in existing_indexes:
            return

        self.pc.create_index(
              name=self.index_name,
              dimension=self.dimension,
              metric=self.metric,
              spec=ServerlessSpec(
                  cloud="aws",
                  region="us-east-1"
              )
          )

    def build_metadata(self,table_name: str,schema: Dict[str, Any],document: str) -> Dict[str, Any]:
        
        table_info = schema.get(table_name, {})

        columns = [
              column.get("name", "")
              for column in table_info.get("columns", [])
          ]

        primary_keys = table_info.get("primary_keys", [])

        foreign_tables = []

        for fk in table_info.get("foreign_keys", []):
            referred_table = fk.get("referred_table")
            if referred_table:
                  foreign_tables.append(referred_table)

        return {
              "table_name": table_name,
              "columns": columns,
              "primary_keys": primary_keys,
              "foreign_tables": foreign_tables,
              "document": document
          }

    def upsert_schema_documents(self,schema: Dict[str, Any],documents: Dict[str, str],namespace: str = "default") -> None:
        table_names = list(documents.keys())
        document_texts = [documents[table_name] for table_name in table_names]

        embeddings = self.embedding_client.embed_documents(document_texts)

        vectors = []

        for table_name, document, embedding in zip(table_names,document_texts,embeddings):
            vectors.append({
                  "id": table_name,
                  "values": embedding,
                  "metadata": self.build_metadata(
                      table_name=table_name,
                      schema=schema,
                      document=document
                  )
              })

        self.index.upsert(
              vectors=vectors,
              namespace=namespace
          )

    def describe_index(self) -> Dict[str, Any]:
          return self.index.describe_index_stats()
