# Data Engineering Workshop Notes

**Discussion guide · Practical examples and scenarios**

These topics are best taught in the order a real data engineering project follows: **understand the data flow → transform the data with SQL → design reliable datasets → store and organize the data efficiently.**

We will use one running example throughout: an e-commerce company that receives customer orders, processes payments, ships products, and prepares sales reports for management.

## Learning roadmap

1. **Data Architecture and Flow**
   - Sources, ingestion, storage, transformation and serving
   - Batch versus streaming
   - ETL versus ELT
2. **Analytical SQL**
   - Joins and CTEs
   - Aggregations and window functions
   - Creating trustworthy analytical datasets
3. **Reliable Data Design**
   - Normalization and dimensional modeling
   - Keys and data grain
   - Schema checks, null rules and reconciliation controls
4. **Portable Storage Formats**
   - Parquet and Delta concepts
   - Partitioning and schema evolution
   - Compression and bronze/silver/gold layers

---

# Module 1 — Data Architecture and Flow

## 1.1 Sources, ingestion, storage, transformation and serving

**Definition:** A data architecture describes how data moves from its original source through processing and storage to the people or applications that use it.

The five main stages are:

1. **Data sources:** Orders, payments, CRM systems and application logs.
2. **Ingestion:** Collecting and transferring data.
3. **Storage:** Persisting raw or processed data in a data lake, warehouse or lakehouse.
4. **Transformation:** Cleaning, validating, joining and aggregating data.
5. **Serving:** Making processed data available through dashboards, reports, APIs and ML models.

**Example:** An online retailer collects order records from its website, loads them into a data platform, cleans the records, calculates daily revenue and displays the results on a sales dashboard.

**Important terms**
- **Data source:** The origin of data, such as a database, CSV file, API or message stream.
- **Ingestion:** Moving data from a source into a data platform.
- **Storage:** Persisting raw or processed data.
- **Transformation:** Changing data into a useful, consistent form.
- **Serving:** Making processed data available to users and applications.

**Discussion scenario:** A manager sees yesterday's sales report showing zero orders. Where could the problem have occurred?

Possible causes include a failed source system, delayed ingestion, an incorrect transformation, a missing partition or a dashboard query error.

**Key lesson:** A data pipeline is an end-to-end system. Correct SQL alone cannot guarantee correct business results.

## 1.2 Batch versus streaming

**Batch processing** processes data collected over a period or in a group.

**Streaming processing** continuously processes or reacts to events as they arrive.

| Aspect | Batch | Streaming |
|---|---|---|
| Input | A group of records | A continuous event flow |
| Latency | Minutes to hours, sometimes longer | Milliseconds to seconds, depending on the system |
| Typical use | Daily sales reports | Fraud alerts and live monitoring |
| Complexity | Often simpler to operate | Requires event-time, late-data and recovery handling |
| Example tools | Scheduled SQL jobs, Spark batch | Kafka, Flink, Spark Structured Streaming |

**Batch example:** Every night at midnight, calculate total sales for the day.

**Streaming example:** Whenever a payment event arrives, update a live transaction-monitoring system.

**Business scenario:** A retailer needs both a daily revenue report and immediate alerts for suspicious payments. A practical design is to use batch processing for the daily report and streaming for the payment alerts.

**Discussion questions**
1. Does every real-time business problem require streaming?
2. What happens if events arrive late or out of order?
3. Could a five-minute micro-batch satisfy a requirement described as “real time”?

The answer depends on the required latency, cost, reliability and business impact.

## 1.3 ETL versus ELT

Both approaches move data from source systems into analytical systems. The main difference is when and where transformation happens.

### ETL — Extract, Transform, Load

1. Extract data from the source.
2. Transform it in a processing layer.
3. Load the prepared data into the target.

**Useful when:** Data must be transformed before entering the target system.

### ELT — Extract, Load, Transform

1. Extract data from the source.
2. Load it into the target platform.
3. Transform it inside the warehouse or lakehouse.

**Useful when:** The target platform can perform scalable transformations.

**Example:** A company receives order CSV files.

- With **ETL**, it cleans the files using a processing engine before loading curated data into a warehouse.
- With **ELT**, it loads source records first and then uses SQL in the warehouse to clean and aggregate them.

**Discussion scenario:** The business frequently changes its definition of “net sales.” Why might ELT be attractive?

Keeping the original records allows the team to apply revised business rules without necessarily extracting the source data again.

**Important distinction:** ELT does not mean loading unvalidated data directly into a production dashboard. Raw data should be retained separately from trusted, consumer-facing datasets.

---

# Module 2 — Analytical SQL

Analytical SQL converts stored records into information that supports business decisions. Students should understand both the SQL syntax and the business meaning of the result.

For the examples below, assume these tables.

### `orders`

| order_id | customer_id | order_date | amount |
|---|---|---|---:|
| 101 | C1 | 2026-10-01 | 1200 |
| 102 | C2 | 2026-10-01 | 800 |
| 103 | C1 | 2026-10-02 | 500 |

### `customers`

| customer_id | customer_name |
|---|---|
| C1 | Ananya |
| C2 | Rahul |

## 2.1 Joins and CTEs

### Joins

**Definition:** A join combines records from two or more tables using a related column or join condition.

| Join | Meaning | Typical use |
|---|---|---|
| `INNER JOIN` | Keeps matching records from both sides | Orders belonging to known customers |
| `LEFT JOIN` | Keeps all left-side records and matching right-side records | Find orders even when customer details are missing |
| `RIGHT JOIN` | Keeps all right-side records and matching left-side records | Retain every record from the right table |
| `FULL OUTER JOIN` | Keeps matching and non-matching records from both sides | Reconcile two datasets |

Example:

```sql
SELECT
    o.order_id,
    c.customer_name,
    o.amount
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id;
```

Expected output:

| order_id | customer_name | amount |
|---|---|---:|
| 101 | Ananya | 1200 |
| 102 | Rahul | 800 |
| 103 | Ananya | 500 |

**Practical scenario:** The order table contains every transaction, while the customer table contains customer profiles. A join combines transactional information with customer details.

**Common mistake:** Joining tables without understanding their relationships can multiply records and inflate revenue. If one order matches three rows in a supposedly unique customer table, that order's amount may be counted three times.

### Common Table Expressions (CTEs)

**Definition:** A CTE is a named query result defined using `WITH`, which makes complex SQL easier to read and organize.

```sql
WITH customer_sales AS (
    SELECT
        customer_id,
        SUM(amount) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_sales
WHERE total_sales > 1000;
```

Expected output:

| customer_id | total_sales |
|---|---:|
| C1 | 1700 |

**Why use CTEs?**
- Break a complex query into logical stages.
- Reuse intermediate results within a statement.
- Make business logic easier to review and maintain.
- Separate aggregation, filtering and final presentation.

**Discussion question:** Is a CTE always faster than a subquery?

No. A CTE is primarily a readability and organization technique. Performance depends on the database engine and query plan.

## 2.2 Aggregations and window functions

### Aggregations

**Definition:** Aggregation summarizes multiple rows into fewer rows using functions such as `SUM`, `COUNT`, `AVG`, `MIN` and `MAX`.

```sql
SELECT
    customer_id,
    SUM(amount) AS total_sales,
    COUNT(*) AS number_of_orders,
    AVG(amount) AS average_order_value
FROM orders
GROUP BY customer_id;
```

Expected output:

| customer_id | total_sales | number_of_orders | average_order_value |
|---|---:|---:|---:|
| C1 | 1700 | 2 | 850 |
| C2 | 800 | 1 | 800 |

**Business uses:** Revenue by customer, average order value, monthly sales, product performance and regional comparisons.

### Window functions

**Definition:** A window function calculates a value across a group of related rows while preserving the individual rows in the output.

```sql
SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
    ) AS customer_total
FROM orders;
```

Expected output:

| order_id | customer_id | amount | customer_total |
|---|---|---:|---:|
| 101 | C1 | 1200 | 1700 |
| 102 | C2 | 800 | 800 |
| 103 | C1 | 500 | 1700 |

Unlike `GROUP BY`, which produces one row per customer here, the window function preserves each order.

Common window functions:
- `ROW_NUMBER()` — assigns a sequential number to rows.
- `RANK()` — ranks rows and leaves gaps after ties.
- `LAG()` — retrieves a preceding row's value.
- `LEAD()` — retrieves a following row's value.
- `SUM() OVER (...)` — calculates a group or running total.

**Business scenario:** The sales manager wants to identify each customer's latest order while retaining the complete order history.

```sql
WITH ranked_orders AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date DESC, order_id DESC
        ) AS rn
    FROM orders
)
SELECT *
FROM ranked_orders
WHERE rn = 1;
```

The `order_id` tie-breaker makes the result deterministic when dates are identical.

**Discussion question:** When would you use `GROUP BY` instead of a window function?

Use `GROUP BY` to summarize data at a new grain. Use a window function when you need calculated context alongside individual records.

## 2.3 Creating trustworthy analytical datasets

**Definition:** A trustworthy analytical dataset is one whose records, business definitions, relationships and calculations are sufficiently validated for the intended decisions.

A dataset is not trustworthy simply because a SQL query executes successfully.

Before accepting a report showing ₹10 lakh in revenue, ask:
1. Were all expected orders ingested?
2. Were cancelled orders treated correctly?
3. Were refunds and discounts handled according to the business definition?
4. Did joins duplicate any transactions?
5. Were amounts stored in consistent currencies?
6. Does the result reconcile with the source system?

### Example: Net sales

Suppose the business defines:

**Net Sales = Gross Sales − Discounts − Refunds**

If gross sales are ₹1,00,000, discounts are ₹5,000 and refunds are ₹3,000:

**Net Sales = ₹92,000**

This definition must be agreed upon by the business. Another company might treat shipping charges, taxes or certain adjustments differently.

### Practical quality checks

| Check | What it detects |
|---|---|
| Completeness | Missing records or fields |
| Uniqueness | Duplicate business keys |
| Validity | Invalid dates, negative quantities or unexpected codes |
| Referential integrity | Orders referencing unknown customers |
| Reconciliation | Differences between source and target totals |
| Freshness | Data that has not arrived on time |

**Workshop exercise:** A report shows 12,000 orders, but the source system shows 11,800. Ask students to investigate duplicate records, date filters, late-arriving data and source-to-target reconciliation before changing the SQL.

**Key lesson:** Trustworthy data requires defined business rules, appropriate SQL and repeatable quality checks.

---

# Module 3 — Reliable Data Design

This module explains how to structure data so that it remains understandable, consistent and useful as systems grow.

## 3.1 Normalization and dimensional modeling basics

### Normalization

**Definition:** Normalization organizes relational data into related tables to reduce unnecessary duplication and prevent inconsistent updates.

Imagine a single table stores order information alongside customer address and product descriptions. If the same customer makes 100 purchases, their address may be repeated 100 times.

A normalized design separates the entities:

- **Customers:** `customer_id`, `name`, `address`
- **Orders:** `order_id`, `customer_id`, `order_date`
- **Order Items:** `order_id`, `product_id`, `quantity`, `unit_price`
- **Products:** `product_id`, `product_name`, `category`

Each table represents a distinct business entity or relationship. Foreign keys connect related records.

**Benefits:** Less redundancy, more consistent updates and clearer data relationships.

**Limitation:** Analytical queries may need several joins. That is one reason analytical systems often use dimensional models.

### Dimensional modeling

**Definition:** Dimensional modeling organizes data into fact tables containing measurable business events and dimension tables describing the context of those events.

- **Fact table:** Stores measures such as quantity, sales amount or transaction count.
- **Dimension table:** Stores descriptive attributes such as customer, product, date or region.

Example: A sales fact table might contain `date_key`, `product_key`, `customer_key`, `quantity` and `sales_amount`. The related dimensions provide the product name, customer segment, date and geographic details.

**Business scenario:** A sales analyst needs to compare monthly revenue by product category and customer region. A star schema makes these analytical queries straightforward.

**Discussion question:** Should every operational database be converted into a star schema?

No. Normalized structures are useful for operational transactions, while dimensional structures are especially useful for analytics. Many platforms use both for different purposes.

## 3.2 Define keys and data grain

### Keys

**Definition:** A key identifies a record or connects it to another record.

- **Primary key:** Uniquely identifies a row in a table.
- **Foreign key:** References a key in another table.
- **Natural key:** Comes from the business domain, such as an externally assigned customer number.
- **Surrogate key:** An artificial identifier, often an integer or generated ID, used within a data model.
- **Composite key:** Uses multiple columns together to identify a row.

Example: `order_id` may uniquely identify an order, while `(order_id, product_id)` may identify an order item if a product appears only once per order. If repeated lines for the same product are allowed, an additional line identifier may be necessary.

### Data grain

**Definition:** Grain states exactly what one row in a dataset represents.

Examples:
- One row per order.
- One row per order item.
- One row per customer per day.
- One row per product per warehouse per hour.

**Why grain matters:** An order with three products can have one order row and three order-item rows. Joining the order total to all three item rows may repeat the total three times.

Suppose an order total is ₹1,500 and it has three items. Summing the repeated order total after the join could produce ₹4,500 instead of ₹1,500.

**Design rule:** Declare the grain before defining measures, keys, joins and aggregations.

**Workshop exercise:** Ask students to design a dataset for “daily product sales by region.” They should state whether one row represents a product-region-day combination and define a key consistent with that grain.

## 3.3 Schema checks, null rules and reconciliation controls

### Schema checks

A schema defines the expected structure of a dataset, including column names, data types and sometimes constraints.

Examples:
- `order_id` must be a string or integer of the expected format.
- `order_date` must be a valid date or timestamp.
- `quantity` must be numeric.
- `amount` must use the expected numeric precision.

Schema checks catch incompatible or unexpected data before it contaminates downstream outputs.

### Null rules

`NULL` represents missing or unknown information; it is not the same as zero or an empty string.

Example: A missing customer phone number may be acceptable, but a missing order identifier generally is not.

Define rules for each field:
- Required or optional?
- Should missing values cause rejection, quarantine or a default?
- Does a missing value have a valid business meaning?
- Can the field be inferred safely from another source?

Avoid replacing every `NULL` with zero. A missing revenue value is not necessarily zero revenue.

### Reconciliation controls

**Definition:** Reconciliation compares related values across systems or pipeline stages to establish that data has been transferred and processed correctly.

Useful controls include:
- Source row count versus target row count.
- Source and target totals for amounts or quantities.
- Counts of rejected and duplicate records.
- Counts grouped by business date or transaction status.
- Checks that accepted and rejected records account for the input, where applicable.

**Scenario:** The payment source reports ₹5,00,000 in successful payments, while the analytical table reports ₹4,80,000. The pipeline should identify the discrepancy and help trace it to missing records, filters, refunds or timing differences.

**Discussion question:** Can source and target row counts differ while the pipeline is still correct?

Yes. Deduplication, filtering, aggregation and intentional exclusions may change the count. The transformation contract must explain and validate the expected difference.

---

# Module 4 — Portable Storage Formats

This module explains how data is physically stored, organized, compressed and evolved over time.

## 4.1 Parquet and Delta concepts

### Apache Parquet

**Definition:** Parquet is an open, column-oriented file format designed for efficient analytical data storage and retrieval.

In a row-oriented format, values from one record are stored together. In a columnar format such as Parquet, values from the same column are stored together in column chunks.

Conceptual example:

**Row-oriented layout**
```text
101, C1, 1200
102, C2, 800
103, C1, 500
```

**Column-oriented layout**
```text
order_id: 101, 102, 103
customer: C1, C2, C1
amount: 1200, 800, 500
```

This is a conceptual illustration, not a byte-level representation of either file format.

**Advantages of Parquet**
- Reads only the columns required by a query.
- Supports efficient compression and encoding.
- Preserves data types and schema information.
- Works with many data processing engines and programming languages.

**Example:** If a sales report needs only `order_date` and `amount` from a dataset with 50 columns, Parquet can allow the query engine to avoid reading the other columns.

**Important limitation:** Parquet is a file format, not a complete transaction-management or table-management system.

### Delta Lake

**Definition:** Delta Lake is a storage layer that adds table-management capabilities to data stored in data lake files, commonly Parquet.

Depending on the implementation and configuration, it provides capabilities such as:
- ACID transactions.
- Consistent table snapshots.
- Schema enforcement and controlled schema evolution.
- Table history and time travel.
- `UPDATE`, `DELETE` and `MERGE` operations.

Delta tables commonly store data in Parquet files and maintain a transaction log describing changes to the table.

**Example:** A retailer receives corrected payment records. Instead of rewriting an entire dataset manually, a supported Delta `MERGE` operation can update matching records and insert new ones transactionally.

**Discussion question:** Is Delta Lake a replacement for Parquet?

Not exactly. Parquet is the underlying data-file format; Delta Lake adds a transactional table layer on top of data files.

## 4.2 Partitioning and schema evolution

### Partitioning

**Definition:** Partitioning organizes data into subsets according to one or more column values so that queries can skip irrelevant data.

For example, a sales dataset might be organized by year and month:

```text
sales/
└── year=2026/
    ├── month=09/
    └── month=10/
```

A query filtering for October 2026 may be able to skip files belonging to other months.

**Benefits:** Better data pruning and more efficient query execution when partitions align with common filters.

**Common mistakes**
- Creating too many tiny partitions.
- Partitioning by a high-cardinality column such as individual transaction ID.
- Using partitions that do not match query patterns.
- Assuming partitioning automatically makes every query faster.

**Scenario:** A company stores five years of sales data and frequently queries one month at a time. Monthly or daily partitioning might help, depending on the data volume and query workload.

### Schema evolution

**Definition:** Schema evolution is the controlled adaptation of a dataset's schema as business requirements change.

Suppose the original orders schema is:

```text
order_id
customer_id
amount
```

Later, the business introduces a `currency` column:

```text
order_id
customer_id
amount
currency
```

The engineering team must decide how older records should be interpreted when `currency` is absent.

Possible policies include:
- Allowing the new nullable column.
- Assigning a valid default only when the business meaning is known.
- Backfilling historical records.
- Rejecting or quarantining incompatible data.
- Versioning the schema when changes are breaking.

**Important distinction:** Schema evolution does not mean accepting every schema change automatically. A new column may be compatible; changing an amount from a decimal to an incompatible string could break downstream consumers.

**Discussion question:** What should happen when a source system renames `customer_id` to `client_id` without warning?

A robust pipeline should detect the unexpected change, apply an explicitly approved mapping or fail safely rather than silently corrupting the output.

## 4.3 Compression and bronze/silver/gold layers

### Compression

**Definition:** Compression reduces the number of bytes required to store data, potentially reducing storage costs and data-transfer time.

Parquet supports compression codecs such as Snappy, Gzip and Zstandard, subject to reader and writer support.

| Codec | General characteristic | Typical consideration |
|---|---|---|
| Snappy | Fast compression and decompression | Often useful for interactive analytics |
| Gzip | Often achieves stronger compression than fast codecs | Can require more CPU |
| Zstandard (Zstd) | Offers configurable compression levels and a useful speed/ratio balance | Benchmark against the workload |

There is no universally best codec. The right choice depends on data characteristics, CPU availability, storage costs and query performance.

**Example:** A company stores 10 TB of historical sales records. Better compression may reduce storage usage, but overly expensive decompression can increase processing time.

**Discussion questions**
- Is the smallest file always the fastest file to query?
- Should frequently accessed data use the same compression settings as archival data?
- How would you benchmark compression choices?

### Bronze, silver and gold layers

**Definition:** The medallion architecture is a layered approach to organizing data according to its processing and quality maturity.

#### Bronze — Raw or landed data
Preserves ingested source data with source metadata and ingestion timestamps. Useful for audit, replay and troubleshooting.

**Example:** Original order events from an application API.

#### Silver — Cleaned and conformed data
Applies schema checks, deduplication, type conversions and standardized business identifiers.

**Example:** Validated orders with duplicates removed and consistent currency fields.

#### Gold — Business-ready data
Provides curated metrics, aggregates and analytical models for business users and applications.

**Example:** Daily net sales by product category and region.

**End-to-end example**
1. **Bronze:** Store the original event and its ingestion metadata.
2. **Silver:** Validate the order ID, check required fields, deduplicate events and standardize the data.
3. **Gold:** Calculate daily revenue by product category, using the approved definition of net sales.

**Why separate the layers?**
- Raw data remains available for investigation and replay.
- Cleaning rules are separated from business reporting rules.
- Multiple gold datasets can be produced from shared silver datasets.
- Data quality can be measured at each stage.

**Important caution:** Bronze, silver and gold are logical layers, not mandatory separate physical systems. Their implementation depends on the platform and operational requirements.

---

# Workshop Discussion and Practical Exercises

Use these activities to check whether students can apply the concepts instead of simply recalling definitions.

## Activity 1 — Choose the architecture (10 minutes)

An e-commerce company needs daily management reports and payment fraud alerts within seconds. Design the data flow and justify batch versus streaming.

## Activity 2 — Write analytical SQL (15 minutes)

Using the sample orders table:
- Calculate total sales per customer.
- Rank orders by customer.
- Identify each customer's latest order.

## Activity 3 — Diagnose unreliable revenue (15 minutes)

A report shows higher revenue than the source system. Investigate grain mismatches, duplicate joins, cancelled orders, refunds, nulls and reconciliation rules.

## Activity 4 — Design a data model (15 minutes)

Design a star schema for sales analytics. Specify the grain of `FactSales`, primary and foreign keys, dimensions and measures.

## Activity 5 — Design the storage pipeline (15 minutes)

Choose Parquet, Delta Lake, partitioning, compression and bronze/silver/gold responsibilities for five years of sales data.

---

# Final Revision Table

| Topic | One concept students should remember |
|---|---|
| Data architecture | Follow the complete path from source to consumer |
| Batch vs streaming | Select processing based on latency and business needs |
| ETL vs ELT | Know when transformation occurs |
| Joins and CTEs | Understand table relationships and structure queries clearly |
| Aggregations and windows | Distinguish summarizing rows from calculating across rows |
| Trustworthy datasets | Validate definitions, quality and reconciliation |
| Normalization and dimensional modeling | Separate operational consistency from analytical convenience |
| Keys and grain | Define what one row represents before building calculations |
| Schema checks and null rules | Make data expectations explicit |
| Parquet and Delta | Distinguish a file format from a transactional table layer |
| Partitioning and schema evolution | Organize data for query efficiency and controlled change |
| Compression and medallion layers | Balance storage efficiency with processing needs and data quality |


