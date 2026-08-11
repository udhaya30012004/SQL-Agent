from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.retrieval.pinecone_sematic_retriever import PineconeSemanticRetriever
from SQL_Agent.retrieval.candidate_merge import CandidateMerger


CONNECTION_STRING = (
      "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
  )


def main():
    engine = connect_database(CONNECTION_STRING)
    schema = extract_schema(engine)

    keyword_selector = TableSelectorWithGraph(schema)
    semantic_retriever = PineconeSemanticRetriever()
    merger = CandidateMerger()

    question = "Top 5 customers by payment"

    keyword_candidates = keyword_selector.select_tables_with_scores(
          question=question,
          top_k=3,
          expand_depth=1
      )

    semantic_candidates = semantic_retriever.search(
          question=question,
          top_k=5
      )

    merged_candidates = merger.merge(
          keyword_candidates=keyword_candidates,
          semantic_candidates=semantic_candidates,
          top_k=8
      )

    print("=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    print("\nKEYWORD CANDIDATES")
    print("-" * 80)
    for candidate in keyword_candidates:
        print(candidate)

    print("\nSEMANTIC CANDIDATES")
    print("-" * 80)
    for candidate in semantic_candidates:
        print(candidate)

    print("\nMERGED CANDIDATES")
    print("-" * 80)
    for candidate in merged_candidates:
        print(candidate)


if __name__ == "__main__":
    main()
