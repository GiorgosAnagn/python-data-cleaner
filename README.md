# Python Data Cleaner

Python Data Cleaner is a reusable Python CLI automation tool for cleaning, validating, and reporting on CSV and XLSX datasets. It is designed for repetitive data-preparation work where raw files need consistent formatting, validation, and a machine-readable summary before they are used elsewhere.

## Problem

Data cleaning often involves repeated manual work: trimming whitespace, standardizing column names, removing empty rows, removing duplicates, checking for invalid values, and producing a record of what changed. This project automates that process in a small, reusable pipeline so the same workflow can be applied repeatedly to tabular data without rewriting the logic each time.

## Features

- CSV and XLSX input
- column-name normalization with collision-safe names
- whitespace and blank-value cleaning
- empty-row removal
- duplicate removal
- explicit numeric-column validation
- missing-value reporting
- numeric statistics
- XLSX output
- strict JSON report
- CLI with useful errors and exit codes
- reusable Python API
- logging

## Example Workflow

```text
messy CSV/XLSX
↓
Python automation
↓
cleaning + validation + reporting
↓
cleaned XLSX + JSON report
```

The workflow starts with a raw CSV or XLSX file. The loader reads the file and preserves text values where appropriate, especially for identifiers that should not be guessed as numeric. The cleaner normalizes column names, trims strings, removes blank and duplicate rows, and validates explicitly declared numeric columns. The exporter writes a cleaned XLSX file and a JSON report containing row counts, missing values, invalid numeric values, and numeric summary statistics.

## Installation

Install the project in editable mode from the repository root:

```bash
python -m pip install -e .
```

## Usage

Run the CLI against the sample dataset:

```bash
python -m python_data_cleaner.cli data/sample_messy_data.csv --output outputs/cleaned_data.xlsx --report outputs/cleaning_report.json
```

The current CLI options are:

- `--output`: required output path for the cleaned XLSX file. It must end with `.xlsx`.
- `--report`: required output path for the JSON report. It must end with `.json`.
- `--sheet-name`: optional sheet name for XLSX input. This is ignored for CSV input.
- `--numeric-column`: optional repeated flag to declare normalized columns that should be validated and converted to numeric values. This is explicit validation, not generic type guessing.
- `--log-level`: logging level for CLI output (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

The CLI also validates that the input file is not overwritten and that the output and report paths are different files.

## Reusable Python API

The project exposes a reusable API through `clean_dataframe(...)`:

```python
import pandas as pd
from python_data_cleaner import clean_dataframe

source = pd.read_csv("data/sample_messy_data.csv")
cleaned_df, report = clean_dataframe(
    source,
    numeric_columns=["amount"],
)
```

This returns the cleaned DataFrame and a JSON-safe report dictionary. The `numeric_columns` argument is used to declare which normalized columns should be validated and converted to numeric values; other non-numeric identifier columns are not guessed automatically.

## Example

The sample dataset currently processes 7 input rows into 5 cleaned rows. The generated XLSX contains the cleaned tabular data, and the JSON report contains the machine-readable summary of cleaning actions, invalid values, missing data, and numeric statistics.

## Testing

The current repository test suite passes with 15 tests.

Run tests with:

```bash
python -m pytest -q
```

## Project Structure

```text
.
├── data/
│   └── sample_messy_data.csv
├── outputs/
│   ├── cleaned_data.xlsx
│   └── cleaning_report.json
├── src/
│   └── python_data_cleaner/
│       ├── __init__.py
│       ├── cleaner.py
│       ├── cli.py
│       ├── exporter.py
│       ├── loader.py
│       └── logging_config.py
├── tests/
│   ├── test_cleaner.py
│   ├── test_cli.py
│   ├── test_exporter.py
│   └── test_loader.py
├── pyproject.toml
├── README.md
```

## Limitations

- Supported input formats are currently `.csv` and `.xlsx` only.
- For XLSX input, the CLI reads a single worksheet, defaulting to the first sheet unless `--sheet-name` is provided.
- Numeric conversion is explicit: only columns listed in `numeric_columns` are validated and converted. The tool does not guess which columns are numeric across the entire file.
- CSV input is loaded with text-preserving behavior so identifiers such as leading-zero values are not silently modified during the initial load.
- The JSON report is designed to remain strict-JSON-safe, which means undefined numeric statistics are represented as `null` rather than `NaN` or `Infinity`.

## Why this project

This project demonstrates practical Python automation for real-world data work: loading files, validating content, normalizing messy inputs, producing clean outputs, creating CLI tooling, and building a reusable API. It also reflects a portfolio-oriented workflow that combines data processing, file handling, testing, documentation, and clear operational behavior in a small, readable codebase.

## License

No license has been specified for this project yet.
