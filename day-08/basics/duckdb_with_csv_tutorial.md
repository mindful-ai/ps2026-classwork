# DuckDB with CSV Files: A Practical Tutorial

DuckDB is an embedded analytical database that lets you query data files directly using SQL. It is particularly useful in data engineering because you can analyze large CSV files without first loading them into a traditional database server.

Think of DuckDB as **SQL for your data files**.

## 1. How DuckDB works with CSV files

DuckDB can query a CSV file directly. You do not have to create a database table or import the file first.

```sql
SELECT *
FROM read_csv_auto('orders.csv');
```

Here, `read_csv_auto()` detects the CSV structure and infers column data types. DuckDB can also query CSV data from Python, join files, and write results to new files.

## 2. Install DuckDB

```bash
pip install duckdb pandas
```

- `duckdb` — SQL analytical engine.
- `pandas` — useful for viewing and manipulating query results in Python.

## 3. Create a sample CSV file

Create a file named `orders.csv`:

```csv
order_id,customer,product,quantity,unit_price,region
101,Asha,Laptop,1,55000,South
102,Ravi,Mouse,2,500,South
103,Meera,Keyboard,1,1500,West
104,Asha,Mouse,1,500,South
105,Ravi,Laptop,1,55000,North
106,Meera,Mouse,3,500,West
```

Save the file in the same directory as your Python program.

## 4. Query a CSV file directly using SQL

Create `duckdb_csv_demo.py`:

```python
import duckdb

result = duckdb.sql("""
    SELECT *
    FROM read_csv_auto('orders.csv')
""")

print(result.df())
```

Run the program:

```bash
python duckdb_csv_demo.py
```

The `.df()` method converts the SQL query result into a Pandas DataFrame.

**What happens internally?**

1. DuckDB opens and inspects the CSV file.
2. It identifies the header and infers column types.
3. It executes the SQL query.
4. It returns the result to Python.

No persistent DuckDB database needs to be created for this example.

## 5. Filter rows and select columns

Find all orders from the South region:

```python
import duckdb

result = duckdb.sql("""
    SELECT order_id, customer, product, region
    FROM read_csv_auto('orders.csv')
    WHERE region = 'South'
""")

print(result.df())
```

Expected result:

| order_id | customer | product | region |
|---:|---|---|---|
| 101 | Asha | Laptop | South |
| 102 | Ravi | Mouse | South |
| 104 | Asha | Mouse | South |

You can use standard SQL clauses such as `WHERE`, `ORDER BY`, `LIMIT`, and `GROUP BY`.

Find the two most expensive products by unit price:

```sql
SELECT product, unit_price
FROM read_csv_auto('orders.csv')
ORDER BY unit_price DESC
LIMIT 2;
```

## 6. Perform analytical calculations

Revenue is quantity multiplied by unit price:

\[
\text{Revenue}=\text{Quantity}\times\text{Unit Price}
\]

Calculate revenue for each order:

```python
import duckdb

result = duckdb.sql("""
    SELECT
        order_id,
        customer,
        product,
        quantity,
        unit_price,
        quantity * unit_price AS revenue
    FROM read_csv_auto('orders.csv')
    ORDER BY revenue DESC
""")

print(result.df())
```

Calculate revenue by region:

```sql
SELECT
    region,
    SUM(quantity * unit_price) AS total_revenue,
    COUNT(*) AS number_of_orders
FROM read_csv_auto('orders.csv')
GROUP BY region
ORDER BY total_revenue DESC;
```

For the sample data:

| Region | Total revenue | Orders |
|---|---:|---:|
| South | 56,500 | 3 |
| North | 55,000 | 1 |
| West | 3,000 | 2 |

The South region has the highest total revenue, at 56,500.

## 7. Query multiple CSV files and join them

Imagine you have two files.

### `customers.csv`

```csv
customer_id,customer,segment
1,Asha,Corporate
2,Ravi,Consumer
3,Meera,Small Business
```

### `orders.csv`

```csv
order_id,customer_id,product,quantity,unit_price
101,1,Laptop,1,55000
102,2,Mouse,2,500
103,3,Keyboard,1,1500
104,1,Mouse,1,500
```

Join these files directly without importing them into tables:

```python
import duckdb

result = duckdb.sql("""
    SELECT
        o.order_id,
        c.customer,
        c.segment,
        o.product,
        o.quantity * o.unit_price AS revenue
    FROM read_csv_auto('orders.csv') AS o
    JOIN read_csv_auto('customers.csv') AS c
        ON o.customer_id = c.customer_id
    ORDER BY o.order_id
""")

print(result.df())
```

DuckDB reads both files and executes the join using `customer_id`. This is useful when customer, order, and product data arrive as separate files.

**Important:** Sections 3–6 and Section 7 use different versions of `orders.csv`. Keep the matching schema in place when running each example, or use different filenames for the two versions.

## 8. Save query results to a CSV file

```python
import duckdb

duckdb.sql("""
    COPY (
        SELECT
            region,
            SUM(quantity * unit_price) AS total_revenue
        FROM read_csv_auto('orders.csv')
        GROUP BY region
    )
    TO 'regional_revenue.csv'
    (HEADER, DELIMITER ',')
""")

print("Output saved to regional_revenue.csv")
```

This creates `regional_revenue.csv` containing the aggregated results.

## 9. Convert CSV to Parquet

Parquet is a columnar file format that is often more efficient than CSV for analytical workloads.

Convert the CSV directly into Parquet:

```python
import duckdb

duckdb.sql("""
    COPY (
        SELECT *
        FROM read_csv_auto('orders.csv')
    )
    TO 'orders.parquet'
    (FORMAT PARQUET)
""")
```

Query the Parquet file:

```python
import duckdb

result = duckdb.sql("""
    SELECT
        region,
        SUM(quantity * unit_price) AS revenue
    FROM read_parquet('orders.parquet')
    GROUP BY region
""")

print(result.df())
```

The SQL remains almost identical. Only the file-reading function changes.

### CSV versus Parquet

- **CSV:** Text-based, human-readable, and widely supported.
- **Parquet:** Columnar, typed, compressed, and often faster for analytical queries.

## 10. Does DuckDB load the entire CSV into memory?

Not necessarily. DuckDB can process CSV files using a streaming, vectorized execution engine and work on chunks rather than requiring the entire dataset to be loaded into a Pandas DataFrame first.

Actual memory usage depends on the query, CSV structure, the amount of data being aggregated or sorted, and available resources.

For example:

```sql
SELECT SUM(quantity * unit_price)
FROM read_csv_auto('large_orders.csv');
```

DuckDB can perform the aggregation within its execution engine rather than creating a Pandas DataFrame containing every row.

## 11. DuckDB versus Pandas

| Feature | DuckDB | Pandas |
|---|---|---|
| Main interface | SQL | Python API |
| Read CSV | `read_csv_auto()` | `read_csv()` |
| Filtering | SQL `WHERE` | Boolean indexing |
| Aggregation | SQL `GROUP BY` | `groupby()` |
| Joining | SQL `JOIN` | `merge()` |
| Large-file analytics | Can process data in chunks internally | Commonly loads the DataFrame into memory |
| Parquet support | Native SQL functions | Supported through compatible engines |

They complement each other. DuckDB performs SQL-heavy analytics, while Pandas is useful for Python-based data manipulation and exploratory analysis.

## 12. Recommended data engineering workflow

1. **Raw CSV files:** Receive orders, customers, and products data.
2. **DuckDB transformation:** Clean, filter, join, aggregate, and validate data using SQL.
3. **Parquet output:** Save processed data in a compressed, columnar format.
4. **Analytics and machine learning:** Use Pandas, visualization tools, feature engineering, or model training on the output datasets.

This workflow starts with raw CSV files, uses DuckDB to transform them with SQL, saves the results as Parquet, and makes those datasets available for downstream analytics and machine learning.

## Summary

DuckDB provides a convenient way to run analytical SQL queries directly against CSV files. You can:

- Read CSV files without importing them into a database table.
- Filter, sort, and aggregate data using SQL.
- Join multiple CSV files.
- Save query results to CSV.
- Convert CSV data into Parquet.
- Integrate SQL analytics with Python and Pandas.

For a data engineering workshop, these capabilities make DuckDB an effective tool for demonstrating data ingestion, transformation, aggregation, and file-format conversion without requiring a separate database server.
