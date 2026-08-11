from pathlib import Path

import pandas as pd


def load_data(file_path: str):

    path = Path(file_path)
    if not path.is_absolute() and not path.exists():
        path = Path(__file__).resolve().parent / path

    extension = (
        path
        .suffix
        .lower()
    )

    if extension == ".csv":

        return pd.read_csv(
            path
        )

    elif extension in [
        ".xlsx",
        ".xls"
    ]:

        return pd.read_excel(
            path
        )

    elif extension == ".parquet":

        return pd.read_parquet(
            path
        )

    elif extension == ".json":

        return pd.read_json(
            path
        )

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )
