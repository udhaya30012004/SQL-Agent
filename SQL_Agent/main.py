"""SQL Agent – Command‑line entry point.

This module provides a small interactive console application that:

1. **Connects** to a PostgreSQL database using the connection string
   defined in ``CONNECTION_STRING``.
2. **Extracts** the database schema via
   :func:`SQL_Agent.schema.schema_extractor.extract_schema`.
3. **Initialises** the LangGraph workflow defined in ``SQL_Agent.graph.workflow``.
4. Enters a **chat loop** where the user can ask natural‑language questions
   about the data. The workflow generates SQL, runs it, optionally creates a
   chart and returns a friendly answer.

The script is deliberately lightweight – all heavy lifting is delegated to the
graph nodes. It is intended for development and debugging; for production you
would typically wrap the workflow in a proper API service.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.graph.workflow import graph


# ==========================================
# DATABASE CONNECTION & SCHEMA EXTRACTION
# ==========================================

CONNECTION_STRING = (
    "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
)

print("Connecting to database…")
engine = connect_database(CONNECTION_STRING)

print("Extracting schema…")
schema = extract_schema(engine)

print("=" * 60)
print("✓ SQL AGENT READY")
print("=" * 60)

print("\nAvailable Tables:")
for table_name in schema.keys():
    print(f"  - {table_name}")

print("\nType 'exit' to quit.\n")


# ==========================================
# MEMORY CONFIG (For persisting state across conversations)
# ==========================================

thread_id = "sql_agent_thread_1"

config = {
    "configurable": {
        "thread_id": thread_id
    }
}


# ==========================================
# CHAT LOOP
# ==========================================

while True:
    # Prompt the user for a question. ``strip`` removes surrounding whitespace.
    question = input("\n❓ Ask Question: ").strip()

    # Exit condition – typing ``exit`` (case‑insensitive) ends the loop.
    if question.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    # Guard against empty input.
    if not question:
        print("⚠️  Please enter a valid question.")
        continue

    try:
        print("\n⏳ Processing your question…")

        # Initialise the LangGraph state. All keys are required by the workflow.
        initial_state = {
            "question": question,
            "schema": schema,
            "sql_query": "",
            "result": None,
            "result_file": None,
            "result_profile": {},
            "chart_spec": {},
            "chart_output": None,
            "chart_error": None,
            "answer": "",
            "selected_tables": [],
            "selected_schema": {},
            "error": None,
        }

        # Run the workflow graph.
        result = graph.invoke(initial_state, config=config)

        # ---------- DISPLAY RESULTS ----------
        print("\n" + "=" * 60)

        if result.get("error"):
            print(f"❌ ERROR: {result['error']}")
        else:
            selected_tables = result.get("selected_tables", [])
            if selected_tables:
                print(f"\n📊 Selected Tables: {', '.join(selected_tables)}")

            sql_query = result.get("sql_query", "")
            if sql_query:
                print(f"\n🔍 Generated SQL:\n{sql_query}")

            answer = result.get("answer", "")
            if answer:
                print(f"\n💡 Answer:\n{answer}")

            chart_spec = result.get("chart_spec", {})

            if chart_spec:
                print(f"\n📈 Chart Spec:\n{chart_spec}")

            chart_output = result.get("chart_output")
            if chart_output:
                print(f"\n📊 Chart Output:\n{chart_output}")
        
                print(f"Type: {chart_output.get('type')}")
                print(f"Chart Type: {chart_output.get('chart_type')}")
                print(f"Title: {chart_output.get('title')}")
                print(f"Path: {chart_output.get('path')}")

            chart_error = result.get("chart_error")
            if chart_error:
                print(f"\n⚠️  Chart Error: {chart_error}")

            

        print("\n" + "=" * 60)

    except Exception as e:  # pragma: no cover – defensive programming
        print(f"\n❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()