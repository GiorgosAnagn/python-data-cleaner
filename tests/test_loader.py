import pandas as pd
import pytest

from python_data_cleaner.loader import load_dataframe


def test_load_dataframe_reads_csv_and_xlsx(tmp_path) -> None:
    expected = pd.DataFrame({"name": ["Ada"], "score": [10]})
    csv_path = tmp_path / "data.csv"
    xlsx_path = tmp_path / "data.xlsx"
    expected.to_csv(csv_path, index=False)
    expected.to_excel(xlsx_path, index=False, engine="openpyxl")

    pd.testing.assert_frame_equal(
        load_dataframe(csv_path), pd.DataFrame({"name": ["Ada"], "score": ["10"]})
    )
    pd.testing.assert_frame_equal(load_dataframe(xlsx_path), expected)


def test_load_dataframe_preserves_leading_zero_csv_identifiers(tmp_path) -> None:
    csv_path = tmp_path / "customers.csv"
    csv_path.write_text("customer_id,amount\n001234,10\n000007,20\n", encoding="utf-8")

    loaded = load_dataframe(csv_path)

    assert loaded["customer_id"].tolist() == ["001234", "000007"]


def test_load_dataframe_rejects_missing_and_unsupported_files(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_dataframe(tmp_path / "missing.csv")
    text_path = tmp_path / "data.txt"
    text_path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        load_dataframe(text_path)
