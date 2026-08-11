"""
Pandas Agent Service

Bridges the FastAPI backend with the LangGraph Pandas Agent workflow.
Handles CSV loading, schema caching, and graph invocation.

Note: ``graph.invoke()`` is synchronous and CPU/IO-bound, so we run it
in a thread via ``asyncio.to_thread()`` to avoid blocking the event loop.
"""

import asyncio
import sys
from pathlib import Path

import pandas as pd
from langchain_core.messages import HumanMessage

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Pandas_Agent.data.csv_loader import load_data
from Pandas_Agent.schema.schema import extract_data
from Pandas_Agent.graph.workflow import graph
from Pandas_Agent.data import data_store

# In-memory caches to keep performance fast across chat rounds
_DF_CACHE = {}
_SCHEMA_CACHE = {}


def _invoke_pandas_agent(
    path_str: str,
    session_id: str,
    question: str,
) -> dict:
    """
    Synchronous helper that performs the actual graph invocation.
    Called inside ``asyncio.to_thread()`` to keep the event loop free.
    """
    # 1. Get DataFrame from cache or load it
    if path_str in _DF_CACHE:
        df = _DF_CACHE[path_str]
    else:
        df = load_data(path_str)
        _DF_CACHE[path_str] = df

    # Bind the DataFrame to the thread/async-safe context variable
    data_store.GLOBAL_DF = df

    # 2. Retrieve or extract schema
    if path_str in _SCHEMA_CACHE:
        schema = _SCHEMA_CACHE[path_str]
    else:
        schema = extract_data(df)
        _SCHEMA_CACHE[path_str] = schema

    # 3. Thread config for LangGraph checkpointer memory
    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    # 4. Build initial query package
    initial_state = {
        "messages": [
            HumanMessage(content=question)
        ],
        "schema": schema,
        "code": "",
        "result": None,
        "last_context": {},
    }

    # 5. Invoke the workflow
    return graph.invoke(initial_state, config=config)


async def run_pandas_agent(
    session_id: str,
    question: str,
    file_path: str,
) -> dict:
    """
    Loads/caches a CSV file, extracts schema, binds the context-safe DataFrame,
    and runs the Pandas Agent LangGraph.

    Uses ``asyncio.to_thread()`` to prevent blocking the FastAPI event loop.
    """
    # Resolve and validate CSV path
    csv_path = Path(file_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at path: {file_path}")

    path_str = str(csv_path.resolve())

    return await asyncio.to_thread(
        _invoke_pandas_agent,
        path_str,
        session_id,
        question,
    )
