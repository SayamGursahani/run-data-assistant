-- Question 1: How consistently do I run?
-- One row per calendar week (weeks start Monday, in UTC), including weeks
-- with zero runs, so gaps in training are visible instead of hidden.
WITH RECURSIVE
bounds AS (
    SELECT date(MIN(run_datetime_utc), '-6 days', 'weekday 1') AS first_week,
           date(MAX(run_datetime_utc), '-6 days', 'weekday 1') AS last_week
    FROM runs
),
weeks(week_start) AS (
    SELECT first_week FROM bounds
    UNION ALL
    SELECT date(week_start, '+7 days')
    FROM weeks, bounds
    WHERE week_start < last_week
),
weekly AS (
    SELECT date(run_datetime_utc, '-6 days', 'weekday 1') AS week_start,
           COUNT(*) AS runs,
           ROUND(SUM(distance_mi), 2) AS total_mi
    FROM runs
    GROUP BY week_start
)
SELECT w.week_start,
       COALESCE(k.runs, 0) AS runs,
       COALESCE(k.total_mi, 0) AS total_mi
FROM weeks w
LEFT JOIN weekly k ON k.week_start = w.week_start
ORDER BY w.week_start;