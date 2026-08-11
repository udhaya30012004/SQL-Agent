"""
SQL Agent Service

Bridges the FastAPI backend with the LangGraph SQL Agent workflow.
Handles database connection, schema caching, and graph invocation.

Note: ``graph.invoke()`` is synchronous and CPU/IO-bound, so we run it
in a thread via ``asyncio.to_thread()`` to avoid blocking the event loop.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path so we can import modules from SQL_Agent and shared
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SQL_Agent.db.db_connector import connect_database
from SQL_Agent.schema.schema_extractor import extract_schema
from SQL_Agent.graph.workflow import graph
from SQL_Agent.db import db_store
from api.app.core.config import settings

# In-memory schema cache to prevent extracting schemas on every request
_SCHEMA_CACHE = {}


def _invoke_sql_agent(
    conn_str: str,
    session_id: str,
    question: str,
    response_mode: str,
) -> dict:
    """
    Synchronous helper that performs the actual graph invocation.
    Called inside ``asyncio.to_thread()`` to keep the event loop free.
    """
    # 1. Get engine and schema
    engine = connect_database(conn_str)

    # Set the engine inside our Thread/Async-safe ContextVar
    db_store.GLOBAL_ENGINE = engine

    # 2. Retrieve or cache the schema
    if conn_str in _SCHEMA_CACHE:
        schema = _SCHEMA_CACHE[conn_str]
    else:
        schema = extract_schema(engine)
        _SCHEMA_CACHE[conn_str] = schema

    # 3. Define Thread ID config for LangGraph memory
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    # 4. Build initial state
    initial_state = {
        "response_mode": response_mode,
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

    # 5. Invoke the LangGraph workflow synchronously
    return graph.invoke(initial_state, config=config)


async def run_sql_agent(
    session_id: str,
    question: str,
    connection_string: str = None,
    response_mode: str = "both",
) -> dict:
    """
    Connects to the database, extracts schema, sets the thread-safe engine context,
    and runs the SQL Agent graph.

    Uses ``asyncio.to_thread()`` to prevent blocking the FastAPI event loop.
    """
    conn_str = connection_string or settings.CONNECTION_STRING

    return await asyncio.to_thread(
        _invoke_sql_agent,
        conn_str,
        session_id,
        question,
        response_mode,
    )
