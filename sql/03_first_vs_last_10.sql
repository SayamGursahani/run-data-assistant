-- Question 2b: Is my pace improving? First 10 runs vs most recent 10 runs.
-- Excludes short runs (< 1 mile). Each run counts equally.
-- avg_distance_mi is included because longer or shorter runs affect pace.
WITH ordered AS (
    SELECT date(run_datetime_utc) AS run_date,
           distance_mi,
           pace_sec_per_mi,
           ROW_NUMBER() OVER (ORDER BY run_datetime_utc ASC)  AS rn_first,
           ROW_NUMBER() OVER (ORDER BY run_datetime_utc DESC) AS rn_last
    FROM runs
    WHERE is_short_run = 0
),
grouped AS (
    SELECT 'First 10 runs' AS run_group, run_date, distance_mi, pace_sec_per_mi
    FROM ordered WHERE rn_first <= 10
    UNION ALL
    SELECT 'Last 10 runs' AS run_group, run_date, distance_mi, pace_sec_per_mi
    FROM ordered WHERE rn_last <= 10
)
SELECT run_group,
       COUNT(*) AS runs,
       MIN(run_date) AS first_run_date,
       MAX(run_date) AS last_run_date,
       ROUND(AVG(distance_mi), 2) AS avg_distance_mi,
       ROUND(AVG(pace_sec_per_mi) / 60, 2) AS avg_pace_min_per_mi,
       printf('%d:%02d',
              CAST(ROUND(AVG(pace_sec_per_mi)) AS INT) / 60,
              CAST(ROUND(AVG(pace_sec_per_mi)) AS INT) % 60) AS avg_pace_mmss,
       ROUND(MIN(pace_sec_per_mi) / 60, 2) AS fastest_pace_min_per_mi,
       ROUND(MAX(pace_sec_per_mi) / 60, 2) AS slowest_pace_min_per_mi
FROM grouped
GROUP BY run_group
ORDER BY MIN(run_date);