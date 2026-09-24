"""Core, reusable DataFrame-cleaning functions."""

from __future__ import annotations

import re
from collections.abc import Sequence
import math
from typing import Any

import numpy as np
import pandas as pd


def _normalise_name(name: object) -> str:
    text = str(name).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unnamed_column"


def _unique_names(names: list[str]) -> list[str]:
    """Return names made unique with predictable numeric suffixes."""
    next_suffix: dict[str, int] = {}
    used: set[str] = set()
    unique: list[str] = []
    for name in names:
        candidate = name
        if candidate in used:
            suffix = next_suffix.get(name, 2)
            candidate = f"{name}_{suffix}"
            while candidate in used:
                suffix += 1
                candidate = f"{name}_{suffix}"
            next_suffix[name] = suffix + 1
        else:
            next_suffix.setdefault(name, 2)
        used.add(candidate)
        unique.append(candidate)
    return unique


def _coerce_numeric_columns(
    frame: pd.DataFrame, numeric_columns: Sequence[str],
) -> dict[str, list[str]]:
    """Coerce declared numeric columns and return their invalid source values."""
    findings: dict[str, list[str]] = {}
    for column in numeric_columns:
        original = frame[column]
        converted = pd.to_numeric(original, errors="coerce")
        non_finite = converted.isin([float("inf"), float("-inf")])
        invalid = original.notna() & (converted.isna() | non_finite)
        if invalid.any():
            findings[column] = [str(value) for value in original[invalid].unique().tolist()]
            converted = converted.mask(invalid)
        frame[column] = converted
    return findings


def _json_number(value: object, metric: str) -> int | float | None:
    """Convert a descriptive-statistic value to a strict-JSON scalar."""
    if metric == "count":
        return int(value)
    numeric_value = float(value)
    return numeric_value if math.isfinite(numeric_value) else None


def _numeric_statistics(series: pd.Series) -> dict[str, int | float | None]:
    """Return strict-JSON-safe summary statistics without warning on invalid data."""
    numeric = pd.to_numeric(series, errors="coerce").astype(float)
    if numeric.isna().all() or numeric.isin([float("inf"), float("-inf")]).any():
        return {
            "count": int(numeric.count()),
            "mean": None,
            "std": None,
            "min": None,
            "25%": None,
            "50%": None,
            "75%": None,
            "max": None,
        }

    finite_values = numeric[np.isfinite(numeric.to_numpy())]
    description = finite_values.describe()
    return {
        str(metric): _json_number(value, str(metric))
        for metric, value in description.items()
    }


def clean_dataframe(
    df: pd.DataFrame, numeric_columns: Sequence[str] | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean a DataFrame and return the cleaned data plus a JSON-safe report.

    The function does not modify ``df``. It normalizes and de-duplicates column
    names, strips text values, treats blank text as missing data, removes fully
    empty rows and duplicate rows.

    Pass normalized column names in ``numeric_columns`` to explicitly validate
    and convert those columns with ``pandas.to_numeric``. Invalid or non-finite
    values become missing values and are listed in ``invalid_numeric_values``.
    Unlisted columns are not guessed to be numeric, so identifiers and codes
    are preserved without being labelled as invalid numeric data.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if isinstance(numeric_columns, str):
        raise TypeError("numeric_columns must be a sequence of column names, not a string")

    cleaned = df.copy()
    original_columns = [str(column) for column in cleaned.columns]
    normalized_columns = _unique_names([_normalise_name(column) for column in cleaned.columns])
    cleaned.columns = normalized_columns

    string_columns = cleaned.select_dtypes(include=["object", "string"]).columns
    for column in string_columns:
        cleaned[column] = cleaned[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        cleaned[column] = cleaned[column].replace("", pd.NA)

    declared_numeric_columns = list(numeric_columns or [])
    unknown_columns = sorted(set(declared_numeric_columns) - set(cleaned.columns))
    if unknown_columns:
        available_columns = ", ".join(str(column) for column in cleaned.columns)
        raise ValueError(
            "Unknown numeric column(s): "
            f"{', '.join(unknown_columns)}. Available normalized columns: {available_columns}"
        )
    invalid_numeric_values = _coerce_numeric_columns(cleaned, declared_numeric_columns)

    initial_rows = len(cleaned)
    cleaned = cleaned.dropna(how="all")
    empty_rows_removed = initial_rows - len(cleaned)

    before_duplicates = len(cleaned)
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    duplicate_rows_removed = before_duplicates - len(cleaned)

    missing_values = {str(column): int(count) for column, count in cleaned.isna().sum().items()}
    numeric_columns = cleaned.select_dtypes(include="number").columns
    statistics: dict[str, dict[str, int | float | None]] = {}
    for column in numeric_columns:
        statistics[str(column)] = _numeric_statistics(cleaned[column])

    report: dict[str, Any] = {
        "rows_before": initial_rows,
        "rows_after": len(cleaned),
        "columns": len(cleaned.columns),
        "column_name_mapping": [
            {"original": original, "normalized": normalized}
            for original, normalized in zip(original_columns, normalized_columns)
        ],
        "empty_rows_removed": empty_rows_removed,
        "duplicate_rows_removed": duplicate_rows_removed,
        "missing_values": missing_values,
        "numeric_columns_checked": declared_numeric_columns,
        "invalid_numeric_values": invalid_numeric_values,
        "numeric_statistics": statistics,
    }
    return cleaned, report
