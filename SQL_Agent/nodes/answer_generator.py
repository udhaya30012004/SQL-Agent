"""
  Answer Generation Node

  Contains the logic for generating business-friendly explanations
  of SQL query results.

  Uses shared LLM service from shared/llm.py
"""

import json
from typing import Any, Dict, List

from SQL_Agent.graph.state import SQLAgentState
from SQL_Agent.prompts.prompts import EXPLANATION_PROMPT


MAX_EXPLANATION_ROWS = 20


def _build_explanation_context(state: SQLAgentState) -> str:
    """
    Build compact explanation context from result_profile and result records.

      The explanation LLM receives:
      - row count
      - columns
      - column type groups
      - first few rows
      - summary statistics
      - chart spec/output metadata

      It does not receive the full raw DataFrame or chart image.
    """
    result_profile = state.get("result_profile", {}) or {}
    result_records = state.get("result") or []
    chart_spec = state.get("chart_spec", {}) or {}
    chart_output = state.get("chart_output") or {}

    explanation_payload: Dict[str, Any] = {
        "row_count": result_profile.get("row_count"),
        "columns": result_profile.get("columns", []),
        "numeric_columns": result_profile.get("numeric_columns", []),
        "categorical_columns": result_profile.get("categorical_columns", []),
        "datetime_columns": result_profile.get("datetime_columns", []),
        "sample_rows": _limit_records(result_records, MAX_EXPLANATION_ROWS),
        "summary": result_profile.get("summary", {}),
        "chart_spec": chart_spec,
        "chart_output": chart_output,
      }

    return json.dumps(explanation_payload, indent=2, default=str)


def _limit_records(records: object, limit: int) -> List[Dict[str, Any]]:
    if not isinstance(records, list):
        return []

    return records[:limit]


def generate_explanation(state: SQLAgentState, llm) -> SQLAgentState:
    """
      Generate a business-friendly explanation of the SQL result.
    """
    if state.get("error"):
        state["answer"] = f"Error: {state['error']}"
        return state

    result_context = _build_explanation_context(state)

    prompt = f"""{EXPLANATION_PROMPT}

  USER QUESTION:
  {state.get("question", "")}

  QUERY RESULT CONTEXT:
  {result_context}
  """

    print("\nRESULT CONTEXT:")
    print(result_context)

    try:
        response = llm.invoke(prompt)
        state["answer"] = response.content.strip()
    except Exception as e:
        state["answer"] = f"Error generating explanation: {str(e)}"

    return state
