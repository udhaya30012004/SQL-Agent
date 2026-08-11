"""
  Test Schema Builder

  This script tests whether rich schema documents are generated correctly.

  It:
  1. Loads schema from schema_cache.json
  2. Builds relationship graph using TableSelectorWithGraph
  3. Builds rich schema documents
  4. Saves all documents into embeddings/schema_documents_output.txt
  5. Prints a short summary
  """

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from SQL_Agent.schema.schema_cache import load_schema_cache
from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.embeddings.schema_documnet_builder import build_schema_documents
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
    relationship_graph = selector.graph

    documents = build_schema_documents(
          schema=schema,
          relationship_graph=relationship_graph
    )

    output_path = Path(__file__).with_name("schema_documents_output1.txt")

    with open(output_path, "w", encoding="utf-8") as file:
        for table_name, document in documents.items():
            file.write(document)
            file.write("\n\n\n")

    print("=" * 60)
    print("SCHEMA BUILDER TEST COMPLETED")
    print("=" * 60)
    print(f"Total tables found: {len(schema)}")
    print(f"Total documents built: {len(documents)}")
    print(f"Output saved to: {output_path}")
    print("=" * 60)

    sample_table = "film"

    if sample_table in documents:
        print(f"\nSample document for table: {sample_table}")
        print("-" * 60)
        print(documents[sample_table])
    else:
        first_table = next(iter(documents))
        print(f"\nSample document for table: {first_table}")
        print("-" * 60)
        print(documents[first_table])


if __name__ == "__main__":
    main()