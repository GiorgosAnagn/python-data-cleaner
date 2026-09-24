"""Output writers for cleaned data and reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def export_cleaned_data(df: pd.DataFrame, path: str | Path) -> Path:
    """Write cleaned data to an XLSX file and return its path."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")
    return output_path


def export_report(report: dict[str, Any], path: str | Path) -> Path:
    """Write a JSON-serializable report to disk and return its path."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False, allow_nan=False)
        file.write("\n")
    return output_path
