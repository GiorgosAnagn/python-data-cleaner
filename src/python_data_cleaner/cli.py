"""Command-line interface for python-data-cleaner."""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from .cleaner import clean_dataframe
from .exporter import export_cleaned_data, export_report
from .loader import load_dataframe
from .logging_config import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Clean a CSV or XLSX file and create Excel and JSON outputs."
    )
    parser.add_argument("input", type=Path, help="Path to a .csv or .xlsx input file")
    parser.add_argument("--output", type=Path, required=True, help="Cleaned .xlsx output path")
    parser.add_argument("--report", type=Path, required=True, help="JSON report output path")
    parser.add_argument("--sheet-name", help="Worksheet name for XLSX input")
    parser.add_argument(
        "--numeric-column",
        action="append",
        default=[],
        metavar="COLUMN",
        help="Normalized column to validate and convert as numeric; repeat as needed",
    )
    parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )
    return parser


def _same_file_path(first: Path, second: Path) -> bool:
    """Return whether paths resolve to the same filesystem location."""
    try:
        if first.exists() and second.exists() and os.path.samefile(first, second):
            return True
    except OSError:
        pass
    return first.resolve() == second.resolve()


def _validate_paths(input_path: Path, output_path: Path, report_path: Path) -> None:
    """Reject unsupported or unsafe output paths before file processing starts."""
    if output_path.suffix.lower() != ".xlsx":
        raise ValueError("--output must have a .xlsx extension")
    if report_path.suffix.lower() != ".json":
        raise ValueError("--report must have a .json extension")
    if _same_file_path(input_path, output_path):
        raise ValueError("--output must not overwrite the input file")
    if _same_file_path(input_path, report_path):
        raise ValueError("--report must not overwrite the input file")
    if _same_file_path(output_path, report_path):
        raise ValueError("--output and --report must be different files")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an appropriate process exit code."""
    args = build_parser().parse_args(argv)
    configure_logging(args.log_level)
    try:
        _validate_paths(args.input, args.output, args.report)
        logging.info("Loading %s", args.input)
        dataframe = load_dataframe(args.input, args.sheet_name)
        cleaned, report = clean_dataframe(dataframe, numeric_columns=args.numeric_column)
        export_cleaned_data(cleaned, args.output)
        export_report(report, args.report)
        logging.info(
            "Completed: %d rows -> %d rows. Wrote %s and %s",
            report["rows_before"], report["rows_after"], args.output, args.report,
        )
        return 0
    except (FileNotFoundError, ValueError, OSError) as error:
        logging.error("%s", error)
        return 2
    except Exception:  # pragma: no cover - last-resort CLI protection
        logging.exception("Unexpected error while cleaning the data")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
