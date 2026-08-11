from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.retrieval.table_selector import TableSelectorWithGraph
from SQL_Agent.db.db_connector import connect_database

CONNECTION_STRING = (
    "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
)

enngine = connect_database(CONNECTION_STRING)


def main():
    schema = extract_schema(enngine)
    question = "Top 5 customers by payment"

    selector = TableSelectorWithGraph(schema)

    print("TABLES ONLY")
    print(selector.select_tables(question))

    print("\nTABLES WITH SCORES")
    results = selector.select_tables_with_scores(question)

    for item in results:
        print(item)


if __name__ == "__main__":
    main()
