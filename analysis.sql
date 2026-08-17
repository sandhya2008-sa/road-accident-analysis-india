-- ============================================================
-- Road Accident Risk Analysis — India (v2)
-- SQL (SQLite) — Data exploration, reliability check, aggregations
-- ============================================================

-- Load accident_prediction_india.csv into a table named `accidents`
-- (via sqlite3 .import, or pandas df.to_sql("accidents", conn))

-- ------------------------------------------------------------
-- 0. DATASET RELIABILITY CHECK
-- Real accident data should NOT have near-equal category counts.
-- If every category is close to equal, the dataset is likely
-- randomly/synthetically generated.
-- ------------------------------------------------------------

SELECT "Weather Conditions" AS category, COUNT(*) AS n
FROM accidents
GROUP BY "Weather Conditions"
ORDER BY n DESC;

SELECT "Road Type" AS category, COUNT(*) AS n
FROM accidents
GROUP BY "Road Type"
ORDER BY n DESC;

-- Records per state — compare to real population spread.
-- If min/max stay in a narrow band regardless of state size,
-- that's a red flag (see Python script for the full check).
SELECT "State Name", COUNT(*) AS total_records
FROM accidents
GROUP BY "State Name"
ORDER BY total_records DESC;


-- ------------------------------------------------------------
-- 1. FATAL ACCIDENTS BY HOUR OF DAY
-- ------------------------------------------------------------
SELECT
  CAST(SUBSTR("Time of Day", 1, INSTR("Time of Day", ':') - 1) AS INTEGER) AS hour,
  COUNT(*) AS fatal_accidents
FROM accidents
WHERE "Accident Severity" = 'Fatal'
GROUP BY hour
ORDER BY fatal_accidents DESC;


-- ------------------------------------------------------------
-- 2. FATAL ACCIDENTS BY WEATHER CONDITION
-- ------------------------------------------------------------
SELECT "Weather Conditions", COUNT(*) AS fatal_accidents
FROM accidents
WHERE "Accident Severity" = 'Fatal'
GROUP BY "Weather Conditions"
ORDER BY fatal_accidents DESC;


-- ------------------------------------------------------------
-- 3. FATAL ACCIDENTS BY STATE — RAW COUNT
-- (kept for comparison; see population-normalized version below)
-- ------------------------------------------------------------
SELECT "State Name", COUNT(*) AS fatal_accidents
FROM accidents
WHERE "Accident Severity" = 'Fatal'
GROUP BY "State Name"
ORDER BY fatal_accidents DESC;


-- ------------------------------------------------------------
-- 3b. FATAL ACCIDENTS BY STATE — POPULATION-NORMALIZED RATE
-- Requires a second table `state_population(state, population)`
-- loaded from population_data.csv (provided alongside this file).
-- ------------------------------------------------------------
SELECT
  a."State Name",
  COUNT(*) AS fatal_accidents,
  p.population,
  ROUND(COUNT(*) * 1.0 / (p.population / 10000000.0), 2) AS fatal_per_crore
FROM accidents a
JOIN state_population p
  ON a."State Name" = p.state
WHERE a."Accident Severity" = 'Fatal'
GROUP BY a."State Name"
ORDER BY fatal_per_crore DESC;


-- ------------------------------------------------------------
-- 4. FATAL ACCIDENTS BY ROAD TYPE
-- ------------------------------------------------------------
SELECT "Road Type", COUNT(*) AS fatal_accidents
FROM accidents
WHERE "Accident Severity" = 'Fatal'
GROUP BY "Road Type"
ORDER BY fatal_accidents DESC;


-- ------------------------------------------------------------
-- 5. FATAL ACCIDENTS BY VEHICLE TYPE INVOLVED
-- NOTE: this column does not distinguish cause vs. victim vehicle.
-- Treat results as co-occurrence counts, not causation.
-- ------------------------------------------------------------
SELECT "Vehicle Type Involved", COUNT(*) AS fatal_accidents
FROM accidents
WHERE "Accident Severity" = 'Fatal'
GROUP BY "Vehicle Type Involved"
ORDER BY fatal_accidents DESC;


-- ------------------------------------------------------------
-- 6. CONTINGENCY TABLES FOR CHI-SQUARE TESTS
-- (exported and tested in Python/R — SQL builds the tables,
-- SQL itself doesn't compute p-values)
-- ------------------------------------------------------------
SELECT "Road Type", "Accident Severity", COUNT(*) AS n
FROM accidents
GROUP BY "Road Type", "Accident Severity";

SELECT "Weather Conditions", "Accident Severity", COUNT(*) AS n
FROM accidents
GROUP BY "Weather Conditions", "Accident Severity";
