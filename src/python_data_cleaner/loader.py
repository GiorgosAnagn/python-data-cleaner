"""Input loading for supported tabular file formats."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_dataframe(path: str | Path, sheet_name: str | None = None) -> pd.DataFrame:
    """Load a CSV or XLSX file into a DataFrame.

    Args:
        path: Input file path.
        sheet_name: Excel worksheet name. Ignored for CSV input.

    CSV values are loaded as text to preserve identifiers such as ``001234``.
    Callers can explicitly convert declared numeric columns through
    ``clean_dataframe(..., numeric_columns=[...])``. XLSX values retain their
    underlying Excel cell values; leading zeroes are preserved only when Excel
    stores the identifier as text.

    Raises:
        FileNotFoundError: If the input file is absent.
        ValueError: If the extension is not CSV or XLSX.
    """
    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(input_path, dtype=str)
    if suffix == ".xlsx":
        # pandas interprets ``sheet_name=None`` as "read every sheet". The CLI
        # needs one DataFrame, so its default is the first worksheet.
        return pd.read_excel(
            input_path, sheet_name=sheet_name if sheet_name is not None else 0, engine="openpyxl"
        )
    raise ValueError("Unsupported input format. Use a .csv or .xlsx file.")
