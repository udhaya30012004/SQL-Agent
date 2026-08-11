from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from SQL_Agent.schema.schema_cache import load_schema_cache
from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.embeddings.schema_documnet_builder import build_schema_documents
from SQL_Agent.embeddings.pinecone_schema_index import PineconeSchemaIndex
from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.schema.schema_extractor import extract_schema


# ==========================================
# DATABASE CONNECTION & SCHEMA EXTRACTION
# ==========================================

CONNECTION_STRING = (
    "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
)

print("Connecting to database...")
engine = connect_database(CONNECTION_STRING)

def main():

    schema = extract_schema(engine)

    if not schema:
        raise ValueError("Schema cache is empty. Please build schema_cache.json first.")

    selector = TableSelectorWithGraph(schema)

    documents = build_schema_documents(
          schema=schema,
          relationship_graph=selector.graph
      )

    pinecone_index = PineconeSchemaIndex()

    pinecone_index.upsert_schema_documents(
          schema=schema,
          documents=documents,
          namespace="default"
      )

    stats = pinecone_index.describe_index()

    print("=" * 60)
    print("PINECONE SCHEMA INDEX COMPLETED")
    print("=" * 60)
    print(f"Schema tables loaded: {len(schema)}")
    print(f"Schema documents embedded and uploaded: {len(documents)}")
    print("Pinecone stats:")
    print(stats)
    print("=" * 60)


if __name__ == "__main__":
    main()
