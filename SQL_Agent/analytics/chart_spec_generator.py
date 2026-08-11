import json
import re
from typing import Any, Dict

from SQL_Agent.analytics.char_spec_validator import validate_chart_spec
from SQL_Agent.graph.state import SQLAgentState
from SQL_Agent.prompts.prompts import CHART_SPEC_PROMPT


def generate_chart_spec(state: SQLAgentState, llm) -> SQLAgentState:
    """
      Generate and validate chart spec using the LLM.

      The LLM receives only:
      - user question
      - result profile

      It does not receive the full raw SQL result.
    """
    if state.get("error"):
        return state

    result_profile = state.get("result_profile", {})

    if not result_profile:
        state["chart_spec"] = _no_chart("Result profile is missing.")
        state["chart_error"] = "Result profile is missing."
        return state

    if result_profile.get("is_empty"):
        state["chart_spec"] = _no_chart("Result is empty.")
        state["chart_error"] = None
        return state

    prompt = f"""{CHART_SPEC_PROMPT}

  USER QUESTION:
  {state.get("question", "")}

  RESULT PROFILE:
  {json.dumps(result_profile, indent=2, default=str)}
  """

    try:
        response = llm.invoke(prompt)
        raw_content = response.content.strip()

        parsed_spec = _parse_json_object(raw_content)

        validated_spec = validate_chart_spec(
              chart_spec=parsed_spec,
              result_profile=result_profile,)

        state["chart_spec"] = validated_spec
        state["chart_error"] = None

    except Exception as e:
        state["chart_spec"] = _no_chart(f"Failed to generate chart spec: {str(e)}")
        state["chart_error"] = str(e)

    return state


def _parse_json_object(raw_content: str) -> Dict[str, Any]:
    """
      Parse a JSON object from LLM response.

      Handles:
      - clean JSON
      - JSON inside markdown code fences
      - extra text around JSON
    """
    if not raw_content:
        raise ValueError("LLM returned empty chart spec.")

    cleaned = raw_content.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)

        if not match:
            raise

        parsed = json.loads(match.group(0))

    if not isinstance(parsed, dict):
        raise ValueError("Chart spec must be a JSON object.")

    return parsed


def _no_chart(reason: str) -> Dict[str, Any]:
    return {
          "render": False,
          "chart_type": None,
          "x_axis": None,
          "y_axis": None,
          "title": None,
          "reason": reason,
      }