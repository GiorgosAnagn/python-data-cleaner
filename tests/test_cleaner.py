import warnings

import pandas as pd
import pytest

from python_data_cleaner import clean_dataframe


def test_clean_dataframe_cleans_data_and_builds_report() -> None:
    source = pd.DataFrame(
        {
            " Customer Name ": [" Alice ", "Bob", "Bob", "   ", "Cara"],
            "Age (years)": ["29", "unknown", "unknown", "", "34"],
            "Score": [10.0, 12.0, 12.0, None, 15.0],
        }
    )

    cleaned, report = clean_dataframe(source, numeric_columns=["age_years"])

    assert list(cleaned.columns) == ["customer_name", "age_years", "score"]
    assert cleaned["customer_name"].tolist() == ["Alice", "Bob", "Cara"]
    assert len(cleaned) == 3
    assert report["empty_rows_removed"] == 1
    assert report["duplicate_rows_removed"] == 1
    assert report["missing_values"] == {"customer_name": 0, "age_years": 1, "score": 0}
    assert report["invalid_numeric_values"] == {"age_years": ["unknown"]}
    assert report["numeric_statistics"]["score"]["mean"] == pytest.approx(12.3333333333)
    assert source.columns.tolist() == [" Customer Name ", "Age (years)", "Score"]


def test_clean_dataframe_makes_duplicate_normalized_names_unique() -> None:
    cleaned, report = clean_dataframe(pd.DataFrame([[1, 2, 3]], columns=["A", "A", "A 2"]))

    assert cleaned.columns.tolist() == ["a", "a_2", "a_2_2"]
    assert cleaned.columns.is_unique
    assert report["column_name_mapping"][2]["normalized"] == "a_2_2"


def test_clean_dataframe_requires_dataframe() -> None:
    with pytest.raises(TypeError, match="pandas DataFrame"):
        clean_dataframe([{"value": 1}])  # type: ignore[arg-type]


def test_explicit_numeric_columns_convert_values_without_guessing_codes() -> None:
    source = pd.DataFrame(
        {"account_code": ["001234", "AB123", "009999"], "amount": ["10", "bad", "20"]}
    )

    cleaned, report = clean_dataframe(source, numeric_columns=["amount"])

    assert cleaned["account_code"].tolist() == ["001234", "AB123", "009999"]
    assert cleaned["amount"].tolist()[0] == 10.0
    assert pd.isna(cleaned["amount"].tolist()[1])
    assert report["numeric_columns_checked"] == ["amount"]
    assert report["invalid_numeric_values"] == {"amount": ["bad"]}
    assert report["numeric_statistics"]["amount"]["count"] == 2


def test_non_finite_and_all_null_numeric_statistics_are_json_safe() -> None:
    all_null = pd.DataFrame({"amount": pd.Series([None, None], dtype="float64")})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _, null_report = clean_dataframe(all_null)
    assert all(
        value is None or metric == "count"
        for metric, value in null_report["numeric_statistics"]["amount"].items()
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _, infinity_report = clean_dataframe(
            pd.DataFrame({"amount": [1.0, float("inf"), float("-inf")]})
        )
    assert all(
        value is None or metric == "count"
        for metric, value in infinity_report["numeric_statistics"]["amount"].items()
    )
