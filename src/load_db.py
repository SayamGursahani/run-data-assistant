"""Load the cleaned runs into a local SQLite database.

Input:  data/processed/runs_clean.csv
Output: data/processed/runs.db   (private, git-ignored)
"""
import sqlite3
from pathlib import Path

import pandas as pd

CSV_PATH = Path("data/processed/runs_clean.csv")
DB_PATH = Path("data/processed/runs.db")


def main() -> None:
    runs = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        runs.to_sql("runs", conn, if_exists="replace", index=False)
        count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    finally:
        conn.close()
    print(f"Loaded {count} rows into table 'runs' in {DB_PATH}")


if __name__ == "__main__":
    main()