-- Phase 5: read-only production checks
SELECT COUNT(*) AS enriched_order_rows FROM read_parquet('data/gold/enriched_orders.parquet');
SELECT order_id, COUNT(*) AS cnt FROM read_parquet('data/gold/enriched_orders.parquet') GROUP BY order_id HAVING COUNT(*) > 1;
SELECT (SELECT COUNT(*) FROM read_parquet('data/bronze/orders.parquet')) AS bronze_rows,
       (SELECT COUNT(*) FROM read_parquet('data/silver/orders.parquet')) AS silver_rows,
       (SELECT COUNT(*) FROM read_parquet('data/gold/enriched_orders.parquet')) AS gold_rows;
SELECT SUM(quantity) AS units, SUM(net_amount) AS net_sales FROM read_parquet('data/gold/enriched_orders.parquet');
