from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator


ChartType = Literal["bar", "line", "pie", "scatter", "histogram"]


class ChartSpec(BaseModel):
    render: bool = Field(description="Whether a chart should be rendered.")
    chart_type: Optional[ChartType] = Field(default=None)
    x_axis: Optional[str] = Field(default=None)
    y_axis: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    reason: str = Field(description="Short reason for the chart decision.")

    @field_validator("chart_type", mode="before")
    @classmethod
    def normalize_chart_type(cls, value):
        if value is None:
            return None

        value = str(value).strip().lower()

        if not value:
            return None

        return value

    @field_validator("x_axis", "y_axis", "title", "reason", mode="before")
    @classmethod
    def normalize_string_fields(cls, value):
        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        return value


def validate_chart_spec(chart_spec: Dict[str, Any],result_profile: Dict[str, Any],) -> Dict[str, Any]:
    """
      Validate and normalize the LLM chart spec.

      Pydantic validates:
      - required fields
      - allowed chart types
      - correct field types

      Custom logic validates:
      - selected axes exist in result columns
      - y_axis is numeric for chart types that need numeric y-axis
    """
    try:
          spec = ChartSpec.model_validate(chart_spec)
    except ValidationError as e:
          return _no_chart(f"Invalid chart spec format: {e.errors()}")

    columns = set(result_profile.get("columns", []))
    numeric_columns = set(result_profile.get("numeric_columns", []))

    if not spec.render:
        return _no_chart(spec.reason or "Chart rendering was not recommended.")

    if not spec.chart_type:
        return _no_chart("chart_type is required when render=true.")

    if spec.chart_type == "histogram":
        if not spec.x_axis:
              return _no_chart("Histogram requires x_axis.")

        if spec.x_axis not in columns:
              return _no_chart(f"x_axis does not exist in result columns: {spec.x_axis}")

        if spec.x_axis not in numeric_columns:
              return _no_chart(f"Histogram x_axis must be numeric: {spec.x_axis}")

        return {
              "render": True,
              "chart_type": spec.chart_type,
              "x_axis": spec.x_axis,
              "y_axis": None,
              "title": spec.title or f"Distribution of {spec.x_axis}",
              "reason": spec.reason,
        }

    if not spec.x_axis:
        return _no_chart("x_axis is required.")

    if spec.x_axis not in columns:
        return _no_chart(f"x_axis does not exist in result columns: {spec.x_axis}")

    if not spec.y_axis:
        return _no_chart("y_axis is required.")

    if spec.y_axis not in columns:
        return _no_chart(f"y_axis does not exist in result columns: {spec.y_axis}")

    if spec.chart_type in {"bar", "line", "pie", "scatter"}:
        if spec.y_axis not in numeric_columns:
            return _no_chart(f"y_axis must be numeric for {spec.chart_type} chart: {spec.y_axis}")

    return {
          "render": True,
          "chart_type": spec.chart_type,
          "x_axis": spec.x_axis,
          "y_axis": spec.y_axis,
          "title": spec.title or _default_title(spec.chart_type, spec.x_axis, spec.y_axis),
          "reason": spec.reason,
    }


def _no_chart(reason: str) -> Dict[str, Any]:
    return {
          "render": False,
          "chart_type": None,
          "x_axis": None,
          "y_axis": None,
          "title": None,
          "reason": reason,
      }


def _default_title(chart_type: str, x_axis: str, y_axis: Optional[str]) -> str:
    if chart_type == "histogram":
        return f"Distribution of {x_axis}"

    return f"{y_axis} by {x_axis}"
