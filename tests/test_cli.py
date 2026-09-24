import json

import pandas as pd

from python_data_cleaner.cli import main


def test_cli_creates_requested_outputs(tmp_path) -> None:
    source = tmp_path / "source.csv"
    pd.DataFrame({" Name ": [" Ada ", " Ada "], "Score": [1, 1]}).to_csv(source, index=False)
    output = tmp_path / "cleaned.xlsx"
    report = tmp_path / "report.json"

    exit_code = main([str(source), "--output", str(output), "--report", str(report)])

    assert exit_code == 0
    assert pd.read_excel(output, engine="openpyxl")["name"].tolist() == ["Ada"]
    assert json.loads(report.read_text(encoding="utf-8"))["duplicate_rows_removed"] == 1


def test_cli_accepts_explicit_numeric_columns(tmp_path) -> None:
    source = tmp_path / "source.csv"
    source.write_text("amount,code\n10,001234\nbad,AB123\n", encoding="utf-8")
    output = tmp_path / "cleaned.xlsx"
    report = tmp_path / "report.json"

    exit_code = main(
        [
            str(source),
            "--output",
            str(output),
            "--report",
            str(report),
            "--numeric-column",
            "amount",
        ]
    )

    assert exit_code == 0
    assert json.loads(report.read_text(encoding="utf-8"))["invalid_numeric_values"] == {"amount": ["bad"]}
    assert pd.read_excel(output, engine="openpyxl")["code"].tolist() == ["001234", "AB123"]


def test_cli_returns_input_error_code(tmp_path) -> None:
    assert main([str(tmp_path / "nope.csv"), "--output", str(tmp_path / "out.xlsx"), "--report", str(tmp_path / "out.json")]) == 2


def test_cli_rejects_unsafe_or_invalid_output_paths(tmp_path) -> None:
    source = tmp_path / "source.xlsx"
    pd.DataFrame({"value": [1]}).to_excel(source, index=False, engine="openpyxl")
    report = tmp_path / "report.json"

    assert main([str(source), "--output", str(source), "--report", str(report)]) == 2
    assert main([str(source), "--output", str(tmp_path / "output.csv"), "--report", str(report)]) == 2
    assert main([str(source), "--output", str(tmp_path / "output.xlsx"), "--report", str(tmp_path / "report.txt")]) == 2


def test_cli_rejects_output_and_report_that_resolve_to_same_file(tmp_path) -> None:
    source = tmp_path / "source.csv"
    source.write_text("value\n1\n", encoding="utf-8")
    output = tmp_path / "output.xlsx"
    report_link = tmp_path / "report.json"
    report_link.symlink_to(output)

    assert main([str(source), "--output", str(output), "--report", str(report_link)]) == 2
