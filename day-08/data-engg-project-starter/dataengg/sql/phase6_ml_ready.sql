SELECT COUNT(*) AS customer_count
FROM read_parquet('data/ml_ready/customer_ml_ready.parquet');

DESCRIBE SELECT * FROM read_parquet('data/ml_ready/customer_ml_ready.parquet');

SELECT COUNT(*) AS customers,
       AVG(total_spend) AS average_spend,
       AVG(total_orders) AS average_orders,
       AVG(recency_days) AS average_recency
FROM read_parquet('data/ml_ready/customer_ml_ready.parquet');

SELECT customer_id, total_orders, total_spend, recency_days
FROM read_parquet('data/ml_ready/customer_ml_ready.parquet')
ORDER BY total_spend DESC LIMIT 10;
