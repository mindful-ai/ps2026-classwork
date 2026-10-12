
-- Phase 4: SQL transformations against the Silver layer.
--
-- These queries are also useful as classroom demonstrations.

-- 1. Enriched order data
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.region,
    p.product_name,
    p.product_category,
    o.quantity,
    o.net_amount
FROM read_parquet('data/silver/orders.parquet') o
LEFT JOIN read_parquet('data/silver/customers.parquet') c
    ON o.customer_id = c.customer_id
LEFT JOIN read_parquet('data/silver/products.parquet') p
    ON o.product_id = p.product_id
LIMIT 20;

-- 2. Customer sales using a CTE
WITH customer_sales AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(net_amount) AS total_spend
    FROM read_parquet('data/silver/orders.parquet')
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    cs.total_orders,
    cs.total_spend
FROM customer_sales cs
JOIN read_parquet('data/silver/customers.parquet') c
    ON cs.customer_id = c.customer_id
ORDER BY cs.total_spend DESC;

-- 3. Product/category performance
SELECT
    p.product_category,
    SUM(o.quantity) AS units,
    SUM(o.net_amount) AS net_sales
FROM read_parquet('data/silver/orders.parquet') o
JOIN read_parquet('data/silver/products.parquet') p
    ON o.product_id = p.product_id
GROUP BY p.product_category
ORDER BY net_sales DESC;

-- 4. Customer order sequence
SELECT
    customer_id,
    order_id,
    order_date,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS order_number
FROM read_parquet('data/silver/orders.parquet')
ORDER BY customer_id, order_date;
