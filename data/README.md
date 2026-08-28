# Data notes

## Raw data

`raw/job_offers_source.xlsx` is the original workbook collected by the author for academic research. It is preserved unchanged for traceability.

## Processed data

- `job_offers_clean.csv` — one standardised record per collected offer;
- `offer_tools.csv` — one row per extracted offer–tool relationship;
- `data_dictionary.csv` — descriptions of processed fields;
- `validation_summary.json` — key data-quality counts;
- `job_market.db` — SQLite database built from the processed CSV files.

The data should be treated as a historical academic sample accessed on 2026-07-09. It is not a live feed of currently active vacancies.
