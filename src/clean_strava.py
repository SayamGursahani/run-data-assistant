"""Clean the Strava activities export into a tidy table of runs.

Input:  data/raw/strava/activities.csv   (private, git-ignored)
Output: data/processed/runs_clean.csv    (private, git-ignored)

All timestamps are kept in UTC (see README).
"""
from pathlib import Path

import pandas as pd

RAW_PATH = Path("data/raw/strava/activities.csv")
OUT_PATH = Path("data/processed/runs_clean.csv")
METERS_PER_MILE = 1609.344
SHORT_RUN_MI = 1.0

# Strava's export repeats some column names; pandas renames the 2nd copy "<name>.1".
COLUMN_MAP = {
    "Activity Date": "run_datetime_utc",
    "Distance.1": "distance_m",
    "Moving Time": "moving_time_s",
    "Elapsed Time": "elapsed_time_s",
    "Elevation Gain": "elevation_gain_m",
    "Average Heart Rate": "avg_heart_rate",
    "Relative Effort.1": "relative_effort",
    "Perceived Exertion": "perceived_exertion",
    "Weather Temperature": "temperature_c",
    "Humidity": "humidity",
}


def check_units(raw_runs: pd.DataFrame) -> None:
    """Confirm our assumptions about units before trusting the numbers."""
    num = raw_runs[["Distance", "Distance.1", "Average Speed", "Moving Time"]].apply(
        pd.to_numeric, errors="coerce"
    )
    dist_gap_m = (num["Distance"] * 1000 - num["Distance.1"]).abs().max()
    pace_from_speed = 1000 / num["Average Speed"]
    pace_from_time = num["Moving Time"] / (num["Distance.1"] / 1000)
    pace_gap_s = (pace_from_speed - pace_from_time).abs().max()
    print(f"Max gap, Distance (km) vs Distance.1 (m): {dist_gap_m:.2f} m")
    print(f"Max gap, pace from speed vs from time: {pace_gap_s:.2f} sec/km")
    if dist_gap_m > 20 or pace_gap_s > 1:
        print("WARNING: units may not be what we assumed. Stop and check.")
    else:
        print("Unit check passed.")


def clean_runs(raw: pd.DataFrame) -> pd.DataFrame:
    runs = raw[raw["Activity Type"] == "Run"].copy()
    runs = runs[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)

    runs["run_datetime_utc"] = pd.to_datetime(
        runs["run_datetime_utc"], utc=True
    ).dt.tz_localize(None)

    numeric_cols = [c for c in runs.columns if c != "run_datetime_utc"]
    runs[numeric_cols] = runs[numeric_cols].apply(pd.to_numeric, errors="coerce")

    runs["distance_mi"] = runs["distance_m"] / METERS_PER_MILE
    runs["pace_sec_per_mi"] = runs["moving_time_s"] / runs["distance_mi"]
    runs["pace_min_per_mi"] = runs["pace_sec_per_mi"] / 60
    runs["is_short_run"] = runs["distance_mi"] < SHORT_RUN_MI

    runs = runs.sort_values("run_datetime_utc").reset_index(drop=True)
    runs.insert(0, "run_number", runs.index + 1)
    return runs


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    raw_runs = raw[raw["Activity Type"] == "Run"]
    print(f"Raw rows: {len(raw)} | runs: {len(raw_runs)}")
    print("Duplicate activity IDs:", raw["Activity ID"].duplicated().sum())
    check_units(raw_runs)

    runs = clean_runs(raw)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    runs.to_csv(OUT_PATH, index=False)

    print(f"\nSaved {len(runs)} runs to {OUT_PATH}")
    print("Date range (UTC):", runs["run_datetime_utc"].min(), "to", runs["run_datetime_utc"].max())
    print(f"Short runs (<{SHORT_RUN_MI} mi):", int(runs["is_short_run"].sum()))
    print("Pace range (min/mi):", round(runs["pace_min_per_mi"].min(), 2), "to", round(runs["pace_min_per_mi"].max(), 2))
    print("\nMissing values per column:")
    print(runs.isna().sum())


if __name__ == "__main__":
    main()