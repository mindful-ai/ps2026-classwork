# Instructor Data Quality Guide

Intentional issues in orders.csv:

| Issue | Approx. scale | Learning objective |
|---|---:|---|
| Exact duplicate rows | 120 | duplicated/drop_duplicates |
| Missing ratings | ~50 | missing-value treatment |
| Missing shipping cost | ~25 | numeric missing values |
| Missing region | ~15 | categorical missing values |
| Inconsistent payment labels | 180 | category normalization |
| Invalid quantity strings | 40 | to_numeric(errors=coerce) |
| Invalid price strings | 40 | numeric conversion |
| Invalid dates | 45 | to_datetime(errors=coerce) |
| Negative quantities | 120 | domain rules |
| Extreme shipping times | 35 | outlier investigation |
| Orphan customer IDs | 15 | referential integrity |
| Orphan product IDs | 15 | referential integrity |
| Non-standard order IDs | 25 | key validation |
| Extreme unit prices | 20 | distribution/outlier analysis |

Do not automatically delete every suspicious value. Require students to document the business rule used for each treatment.

Recommended derived columns:
- gross_amount = quantity * unit_price
- discount_amount = gross_amount * discount_pct / 100
- net_amount = gross_amount - discount_amount
- total_amount = net_amount + shipping_cost

Recommended merge sequence:
1. orders -> customers on customer_id
2. orders -> products on product_id

Record row counts before and after each merge and validate key relationships.


