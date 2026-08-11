from pathlib import Path
from typing import Any, Dict
import re

import pandas as pd
import plotly.express as px

from SQL_Agent.graph.state import SQLAgentState


CHART_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "charts"


def render_chart_from_state(state: SQLAgentState) -> SQLAgentState:
    """
    Render an interactive Plotly chart from state["chart_spec"] and state["result"].

    The chart is saved as an HTML file.
    The output metadata is stored in state["chart_output"].
    """
    chart_spec = state.get("chart_spec", {})

    if not chart_spec or not chart_spec.get("render"):
        state["chart_output"] = None
        return state

    records = state.get("result") or []

    if not records:
        state["chart_output"] = None
        state["chart_error"] = "No result records available for chart rendering."
        return state

    try:
        df = pd.DataFrame(records)

        chart_output = render_chart(
            df=df,
            chart_spec=chart_spec,
        )

        state["chart_output"] = chart_output
        state["chart_error"] = None

    except Exception as e:
        state["chart_output"] = None
        state["chart_error"] = f"Chart rendering failed: {str(e)}"

    return state


def render_chart(df: pd.DataFrame, chart_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatch to the correct Plotly chart renderer.
    """
    chart_type = chart_spec.get("chart_type")
    x_axis = chart_spec.get("x_axis")
    y_axis = chart_spec.get("y_axis")
    title = chart_spec.get("title") or "Chart"

    if chart_type == "bar":
        fig = _bar_chart(df, x_axis, y_axis, title)
    elif chart_type == "line":
        fig = _line_chart(df, x_axis, y_axis, title)
    elif chart_type == "pie":
        fig = _pie_chart(df, x_axis, y_axis, title)
    elif chart_type == "scatter":
        fig = _scatter_chart(df, x_axis, y_axis, title)
    elif chart_type == "histogram":
        fig = _histogram(df, x_axis, title)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    _apply_theme(fig, title, x_axis, y_axis)

    output_path = _save_chart_html(fig, chart_type)

    return {
        "type": "plotly_html",
        "path": str(output_path),
        "chart_type": chart_type,
        "title": title,
    }


def _bar_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str):
    return px.bar(
        df,
        x=x_axis,
        y=y_axis,
        title=title,
        text=y_axis,
        color=x_axis,
    )


def _line_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str):
    return px.line(
        df,
        x=x_axis,
        y=y_axis,
        title=title,
        markers=True,
    )


def _pie_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str):
    return px.pie(
        df,
        names=x_axis,
        values=y_axis,
        title=title,
        hole=0.35,
    )


def _scatter_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str):
    return px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        title=title,
        size=y_axis,
        color=y_axis,
    )


def _histogram(df: pd.DataFrame, x_axis: str, title: str):
    return px.histogram(
        df,
        x=x_axis,
        title=title,
        nbins=30,
    )


def _apply_theme(fig, title: str, x_axis: str | None = None, y_axis: str | None = None) -> None:
    """
    Apply a clean interactive Plotly design.
    """
    fig.update_layout(
        template="plotly_white",
        title={
            "text": f"<b>{title}</b>",
            "x": 0.02,
            "xanchor": "left",
            "font": {
                "size": 22,
                "family": "Arial",
            },
        },
        font={
            "family": "Arial",
            "size": 13,
        },
        hovermode="closest",
        margin={
            "l": 60,
            "r": 30,
            "t": 80,
            "b": 60,
        },
        legend_title_text="",
    )

    if x_axis:
        fig.update_xaxes(
            title_text=f"<b>{x_axis}</b>",
            title_font={"family": "Arial", "size": 15},
            tickfont={"family": "Arial", "size": 12},
        )

    if y_axis:
        fig.update_yaxes(
            title_text=f"<b>{y_axis}</b>",
            title_font={"family": "Arial", "size": 15},
            tickfont={"family": "Arial", "size": 12},
        )

    fig.update_traces(hovertemplate=None)


def _save_chart_html(fig, chart_type: str) -> Path:
    CHART_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_chart_type = re.sub(r"[^a-zA-Z0-9]+", "_", chart_type.lower()).strip("_")
    base_name = f"{safe_chart_type}_graph"
    output_path = CHART_OUTPUT_DIR / f"{base_name}.html"

    counter = 2
    while output_path.exists():
        output_path = CHART_OUTPUT_DIR / f"{base_name}_{counter}.html"
        counter += 1

    fig.write_html(
        str(output_path),
        include_plotlyjs="cdn",
        full_html=True,
    )

    return output_path