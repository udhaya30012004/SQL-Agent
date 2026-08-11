from typing import Any, Dict, List

import pandas as pd


MAX_SAMPLE_ROWS = 10
MAX_UNIQUE_VALUES = 20


def _safe_value(value: Any) -> Any:
    """
      Convert pandas/numpy values into JSON-safe Python values.
    """
    if pd.isna(value):
          return None

    if hasattr(value, "item"):
        try:
              return value.item()
        except Exception:
              pass

    if hasattr(value, "isoformat"):
        try:
              return value.isoformat()
        except Exception:
              pass

    return value


def _safe_records(df: pd.DataFrame, limit: int = MAX_SAMPLE_ROWS) -> List[Dict[str, Any]]:
    """
      Convert the first rows of a DataFrame into JSON-safe records.

      This is similar to df.head(limit), but converted into list[dict].
    """
    records = df.head(limit).to_dict(orient="records")

    return [
          {
              column: _safe_value(value)
              for column, value in row.items()
          }
          for row in records
      ]


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
      Build a compact DataFrame profile for analytics and LLM chart selection.

      This avoids sending the full raw SQL result to the LLM.
      The LLM receives:
      - row count
      - column names
      - detected column types
      - first few rows
      - summary statistics
    """
    if df is None:
          return {
              "row_count": 0,
              "column_count": 0,
              "columns": [],
              "numeric_columns": [],
              "categorical_columns": [],
              "datetime_columns": [],
              "boolean_columns": [],
              "sample_rows": [],
              "summary": {},
              "is_empty": True,
          }

    if df.empty:
          return {
              "row_count": 0,
              "column_count": len(df.columns),
              "columns": list(df.columns),
              "numeric_columns": [],
              "categorical_columns": [],
              "datetime_columns": [],
              "boolean_columns": [],
              "sample_rows": [],
              "summary": {},
              "is_empty": True,
          }

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    boolean_columns = df.select_dtypes(include=["bool"]).columns.tolist()

    categorical_columns = [
        column
        for column in df.columns
        if column not in numeric_columns
        and column not in datetime_columns
        and column not in boolean_columns
    ]

    summary: Dict[str, Any] = {}

    for column in df.columns:
        series = df[column]

        column_summary: Dict[str, Any] = {
              "dtype": str(series.dtype),
              "null_count": int(series.isna().sum()),
              "non_null_count": int(series.notna().sum()),
              "unique_count": int(series.nunique(dropna=True)),
          }

        if column in numeric_columns:
              column_summary.update({
                  "min": _safe_value(series.min()),
                  "max": _safe_value(series.max()),
                  "mean": _safe_value(series.mean()),
                  "median": _safe_value(series.median()),
              })

        elif column in datetime_columns:
              column_summary.update({
                  "min": _safe_value(series.min()),
                  "max": _safe_value(series.max()),
              })

        else:
              unique_values = series.dropna().astype(str).unique().tolist()
              column_summary["sample_values"] = unique_values[:MAX_UNIQUE_VALUES]

        summary[column] = column_summary

    return {
          "row_count": int(len(df)),
          "column_count": int(len(df.columns)),
          "columns": list(df.columns),
          "numeric_columns": numeric_columns,
          "categorical_columns": categorical_columns,
          "datetime_columns": datetime_columns,
          "boolean_columns": boolean_columns,
          "sample_rows": _safe_records(df),
          "summary": summary,
          "is_empty": False,
      }
