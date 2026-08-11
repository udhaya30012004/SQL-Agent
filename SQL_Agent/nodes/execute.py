'''
  this file executes the generated query from the llm to the database to
  fetch the results
'''

import re

import pandas as pd
from sqlalchemy import text

from SQL_Agent.db import db_store


MAX_EXECUTION_ROWS = 10000


def clean_query(query: str) -> str:
    """
      Clean the SQL query by removing markdown code block syntax if present.
    """
    query = query.strip()

    if query.startswith("```"):
        lines = query.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        query = "\n".join(lines).strip()

    return query


def repair_postgres_enum_casts(query: str, error: Exception) -> str:
    """
      Retry helper for PostgreSQL enum/custom type text operations.
    """
    error_text = str(error).lower()
    should_repair = (
        "function lower(" in error_text and "does not exist" in error_text
    ) or "invalid input value for enum" in error_text

    if not should_repair:
        return query

    repaired = re.sub(
        r"\bLOWER\(\s*([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)?)\s*\)",
        lambda match: f"LOWER({match.group(1)}::text)",
        query,
        flags=re.IGNORECASE,
    )
    repaired = re.sub(
        r"\bCOALESCE\(\s*([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)?)\s*,\s*('(?:Unknown|unknown)')\s*\)",
        lambda match: f"COALESCE({match.group(1)}::text, {match.group(2)})",
        repaired,
        flags=re.IGNORECASE,
    )

    return repaired


def execute_sql(query: str) -> pd.DataFrame:
    """
      Execute SQL and return a pandas DataFrame.

      The returned DataFrame is limited for safety, but the limit is now large
      enough for analytics and plotting workflows.

      Important:
      - Do not send this full DataFrame to the LLM.
      - Use result_profile for LLM context.
      - Use the DataFrame/list records for plotting.
    """
    engine = db_store.GLOBAL_ENGINE

    if engine is None:
        raise ValueError("DataBase connection not found")

    cleaned_query = clean_query(query)

    try:
        try:
            result = pd.read_sql(text(cleaned_query), engine)
        except Exception as e:
            repaired_query = repair_postgres_enum_casts(cleaned_query, e)
            if repaired_query == cleaned_query:
                raise
            result = pd.read_sql(text(repaired_query), engine)

        if len(result) > MAX_EXECUTION_ROWS:
            result = result.head(MAX_EXECUTION_ROWS)

        return result

    except Exception as e:
        raise Exception(f"SQL Execution Failed: {str(e)}")
