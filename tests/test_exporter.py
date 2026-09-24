import json

import pandas as pd
import pytest

from python_data_cleaner.exporter import export_cleaned_data, export_report


def test_exporters_write_readable_xlsx_and_json(tmp_path) -> None:
    dataframe = pd.DataFrame({"name": ["Ada"], "score": [10]})
    report = {"rows_after": 1, "missing_values": {"score": 0}}
    xlsx_path = export_cleaned_data(dataframe, tmp_path / "nested" / "cleaned.xlsx")
    json_path = export_report(report, tmp_path / "nested" / "report.json")

    assert xlsx_path.is_file()
    pd.testing.assert_frame_equal(pd.read_excel(xlsx_path, engine="openpyxl"), dataframe)
    assert json.loads(json_path.read_text(encoding="utf-8")) == report


def test_export_report_writes_strict_json_and_rejects_non_finite_values(tmp_path) -> None:
    json_path = export_report({"value": None}, tmp_path / "report.json")

    def reject_non_standard_constant(value: str) -> None:
        raise ValueError(f"Invalid JSON constant: {value}")

    assert json.loads(json_path.read_text(encoding="utf-8"), parse_constant=reject_non_standard_constant) == {
        "value": None
    }
    with pytest.raises(ValueError, match="Out of range"):
        export_report({"value": float("nan")}, tmp_path / "invalid.json")
