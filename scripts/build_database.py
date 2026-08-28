"""Create a portable SQLite database from the processed CSV files."""

from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DIR / "job_market.db"


def main() -> None:
    offers = pd.read_csv(PROCESSED_DIR / "job_offers_clean.csv")
    tools = pd.read_csv(PROCESSED_DIR / "offer_tools.csv")
    schema = (PROJECT_ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(schema)
        offers.to_sql("job_offers", connection, if_exists="append", index=False)
        tools.to_sql("offer_tools", connection, if_exists="append", index=False)

    print(f"Created {DATABASE_PATH}")


if __name__ == "__main__":
    main()
