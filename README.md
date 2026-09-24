# python-data-cleaner

A small Python CLI and reusable library for cleaning CSV and XLSX files. It
normalizes column names, removes empty and duplicate rows, trims text values,
and writes an Excel file plus a JSON cleaning report.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Use from the command line

```bash
python-data-cleaner data/sample_messy_data.csv \
  --output outputs/cleaned_data.xlsx \
  --report outputs/cleaning_report.json
```

For XLSX input, optionally choose a sheet with `--sheet-name`.

## Use as a library

```python
import pandas as pd
from python_data_cleaner import clean_dataframe

cleaned_df, report = clean_dataframe(pd.read_csv("source.csv"))
```

`report` is JSON-serializable.
