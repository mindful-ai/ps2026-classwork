\
-- Phase 1: Data & SQL Foundations
-- DuckDB reads the mapped CSV files directly.

CREATE OR REPLACE VIEW customers AS
SELECT * FROM read_csv_auto('data/phase1/customers_mapped.csv');

CREATE OR REPLACE VIEW products AS
SELECT * FROM read_csv_auto('data/phase1/products_mapped.csv');

CREATE OR REPLACE VIEW orders AS
SELECT * FROM read_csv_auto('data/phase1/orders_mapped.csv');

-- 1. Basic inspection
SELECT * FROM customers LIMIT 10;
SELECT * FROM products LIMIT 10;
SELECT * FROM orders LIMIT 10;

-- 2. Establish grain
SELECT
    COUNT(*) AS order_lines,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(DISTINCT customer_id) AS distinct_customers,
    COUNT(DISTINCT product_id) AS distinct_products
FROM orders;

-- 3. Join orders to customers and products
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.region,
    p.product_name,
    p.product_category,
    o.quantity,
    o.unit_price,
    o.discount_pct
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN products p ON o.product_id = p.product_id
LIMIT 20;

-- 4. Revenue by product
SELECT
    p.product_name,
    SUM(o.quantity * o.unit_price) AS gross_sales
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY gross_sales DESC;

-- 5. Revenue by customer
SELECT
    c.customer_name,
    SUM(o.quantity * o.unit_price) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY total_spend DESC;

-- 6. CTE: customer sales
WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(quantity * unit_price) AS total_spend,
        COUNT(DISTINCT order_id) AS total_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    cs.total_orders,
    cs.total_spend
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_spend DESC;

-- 7. Window function: customer order sequence
SELECT
    customer_id,
    order_id,
    order_date,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS customer_order_number
FROM orders
ORDER BY customer_id, order_date;

-- 8. Window function: previous order
SELECT
    customer_id,
    order_id,
    order_date,
    LAG(order_date) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS previous_order_date
FROM orders;

-- 9. Ranking customers
WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(quantity * unit_price) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    cs.total_spend,
    RANK() OVER (ORDER BY cs.total_spend DESC) AS spend_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY spend_rank;
