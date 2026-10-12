
-- DuckDB can query Parquet directly.
-- Run from the project root with DuckDB.

SELECT *
FROM read_parquet('data/parquet/orders.parquet')
LIMIT 10;

-- Aggregation without loading the complete dataset into Pandas.
SELECT
    product_id,
    SUM(quantity) AS units,
    SUM(quantity * unit_price) AS gross_sales
FROM read_parquet('data/parquet/orders.parquet')
GROUP BY product_id
ORDER BY gross_sales DESC;

-- Query partitioned Parquet directly.
SELECT
    COUNT(*) AS rows_in_2026
FROM read_parquet('data/partitioned_orders/**/*.parquet')
WHERE order_year = 2026;
