# Phase 1 Teaching Notes

## Business model

- `customers.customer_id` is the customer primary key.
- `products.product_id` is the product primary key.
- `orders.order_id` identifies an order.
- `orders.customer_id` references customers.
- `orders.product_id` references products.

## Grain

For this project, the intended grain of `orders` is:

> One row = one order-product line.

Therefore, an order can have multiple rows when it contains multiple products.

## Why IDs are preserved

The mapping layer changes presentation/business names, not relational identity.
This makes joins and downstream transformations stable.

## SQL concepts demonstrated

- SELECT / filtering
- GROUP BY and aggregations
- INNER/LEFT JOIN
- CTE
- ROW_NUMBER
- LAG
- RANK

## ML connection

The customer-level CTE/window examples are the starting point for future
feature engineering, especially:

- total_orders
- total_spend
- average_order_value
- previous_order_date
- recency
