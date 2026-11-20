"""Run every .sql file in sql/ and export each result as a CSV.

Input:  sql/*.sql and data/processed/runs.db
Output: data/exports/<query_name>.csv   (private, git-ignored)
"""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/processed/runs.db")
SQL_DIR = Path("sql")
OUT_DIR = Path("data/exports")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        for sql_file in sorted(SQL_DIR.glob("*.sql")):
            result = pd.read_sql_query(sql_file.read_text(), conn)
            out_path = OUT_DIR / f"{sql_file.stem}.csv"
            result.to_csv(out_path, index=False)
            print(f"{sql_file.name}: {len(result)} rows -> {out_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()