"""Graph node definitions for the SQL Agent workflow.

Each function receives a :class:`SQLAgentState` dictionary, performs a single
step, and returns the (potentially mutated) state.  The nodes are wired together
by the LangGraph workflow defined in ``SQL_Agent.graph.workflow``.
"""

from shared.llm import get_llm
from SQL_Agent.nodes.sql_generator import generate_sql
from SQL_Agent.nodes.validate import validate_query
from SQL_Agent.nodes.execute import execute_sql
from SQL_Agent.nodes.answer_generator import generate_explanation
from SQL_Agent.graph.state import SQLAgentState
from SQL_Agent.analytics.result_profile import profile_dataframe
from SQL_Agent.analytics.chart_spec_generator import generate_chart_spec
from SQL_Agent.analytics.chart_render import render_chart_from_state

# Initialise the LLM once at module import time – it is reused by multiple nodes.
llm = get_llm()


def generation_node(state: SQLAgentState):
    """Generate a SQL query from the user's natural‑language question.

    Delegates to :func:`SQL_Agent.nodes.sql_generator.generate_sql` which uses
    the LLM to produce the query.
    """
    return generate_sql(state, llm)


def validation_node(state: SQLAgentState):
    """Validate the generated SQL query before execution.

    If ``state['error']`` is already set, the node is a no‑op.
    """
    if state.get("error"):
        return state

    try:
        cleaned_query = validate_query(state.get("sql_query", ""))
        state["sql_query"] = cleaned_query
    except Exception as e:  # pragma: no cover – defensive
        state["error"] = f"SQL Validation Error: {str(e)}"

    return state


def execution_node(state: SQLAgentState):
    """Execute the validated SQL and store results in the state.

    The pandas ``DataFrame`` is converted to a list‑of‑dicts for serialisation
    and a compact profile is generated for downstream analytics.
    """
    if state.get("error"):
        return state

    try:
        result_df = execute_sql(state.get("sql_query", ""))
        state["result"] = result_df.to_dict(orient="records")
        state["result_profile"] = profile_dataframe(result_df)
    except Exception as e:  # pragma: no cover – defensive
        state["error"] = f"SQL Execution Error: {str(e)}"

    return state


def analytics_node(state: SQLAgentState):
    """Generate a chart spec and render an interactive Plotly chart.

    The node first asks the LLM for a chart specification based on the result
    profile, then renders the chart and stores metadata in ``state['chart_output']``.
    """
    if state.get("error"):
        return state

    state = generate_chart_spec(state, llm)
    state = render_chart_from_state(state)
    return state


def explanation_node(state: SQLAgentState):
    """Generate a business‑friendly explanation of the SQL result.

    This is the second LLM call in the workflow.  It uses the original question
    and the query result (or any error) to produce a natural‑language answer.
    """
    return generate_explanation(state, llm)