-- Question 2a: Is my pace improving? Per-run pace plus a rolling average.
-- Excludes short runs (< 1 mile). The rolling average covers the last 5 runs
-- and is left empty until 5 runs exist, so early points aren't misleading.
-- window_span_days shows how many days the 5 runs cover (long = a gap).
WITH pace_runs AS (
    SELECT run_number,
           date(run_datetime_utc) AS run_date,
           distance_mi,
           pace_sec_per_mi
    FROM runs
    WHERE is_short_run = 0
),
rolling AS (
    SELECT run_number,
           run_date,
           distance_mi,
           pace_sec_per_mi,
           AVG(pace_sec_per_mi) OVER w AS roll_sec,
           COUNT(*) OVER w AS runs_in_window,
           FIRST_VALUE(run_date) OVER w AS window_start_date
    FROM pace_runs
    WINDOW w AS (ORDER BY run_number ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
)
SELECT run_number,
       run_date,
       ROUND(distance_mi, 2) AS distance_mi,
       ROUND(pace_sec_per_mi / 60, 2) AS pace_min_per_mi,
       printf('%d:%02d',
              CAST(ROUND(pace_sec_per_mi) AS INT) / 60,
              CAST(ROUND(pace_sec_per_mi) AS INT) % 60) AS pace_mmss,
       CASE WHEN runs_in_window = 5
            THEN ROUND(roll_sec / 60, 2) END AS rolling_5_pace_min_per_mi,
       CASE WHEN runs_in_window = 5
            THEN CAST(julianday(run_date) - julianday(window_start_date) AS INT)
       END AS window_span_days
FROM rolling
ORDER BY run_number;