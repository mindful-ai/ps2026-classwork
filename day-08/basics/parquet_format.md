# Apache Parquet — Student Notes

## 1. What is Parquet?

**Apache Parquet is an open-source, column-oriented file format designed to store structured data efficiently, especially for analytical workloads.**

It is widely used in data engineering with tools such as Apache Spark, Pandas, DuckDB, and cloud data platforms.

Parquet is particularly useful when datasets contain millions of rows and analytical queries need to read only a few columns.

### Key characteristics

- **Columnar storage:** Organizes data by column rather than primarily by row.
- **Compression and encoding:** Can reduce storage requirements.
- **Efficient analytical queries:** Allows engines to read only the required columns.
- **Schema information:** Stores column names and data types.
- **Interoperability:** Supported by many data processing tools.

## 2. Row-oriented versus column-oriented storage

Suppose an e-commerce company has this dataset:

| Order ID | Customer | City | Amount |
|---|---|---|---:|
| 101 | Ananya | Bengaluru | 1200 |
| 102 | Rahul | Mysuru | 800 |
| 103 | Priya | Bengaluru | 1500 |

### Row-oriented representation

A CSV file typically represents records row by row:

```text
101,Ananya,Bengaluru,1200
102,Rahul,Mysuru,800
103,Priya,Bengaluru,1500
```

### Column-oriented representation

Conceptually, Parquet organizes values into column chunks:

```text
Order ID: 101, 102, 103
Customer: Ananya, Rahul, Priya
City: Bengaluru, Mysuru, Bengaluru
Amount: 1200, 800, 1500
```

This is an illustration of the storage concept, not the literal binary contents of a Parquet file.

**Why does this matter?**

Suppose a manager asks:

> What is the total sales amount?

The query only needs the `Amount` column. A columnar format allows a query engine to avoid reading the other columns when its execution plan can use column pruning.

## 3. How Parquet helps in data engineering

### 3.1 Less data read for analytical queries

If a dataset has 80 columns but a report uses only 3, a Parquet-aware engine can read only those required columns.

This is called **column pruning**.

### 3.2 Compression can reduce storage

Values in the same column often share patterns. For example, a `City` column might contain many repeated values such as Bengaluru, Mysuru and Chennai. Encoding and compression can store such data efficiently.

Actual storage savings depend on the data, codec and settings; Parquet is not guaranteed to be smaller for every dataset.

### 3.3 Data types are retained

CSV generally stores values as text and relies on software to infer or assign types when reading. Parquet stores schema information, such as:

- `order_id`: integer
- `order_date`: date or timestamp
- `amount`: numeric
- `customer`: string

This can reduce ambiguity, although the consuming application must still interpret the schema correctly.

### 3.4 Works across data tools

A Parquet file written by one supported tool can often be read by another. This makes it useful for data lakes and data pipelines that use multiple engines.

### 3.5 Supports large analytical datasets

Parquet is well suited to analytical data such as sales history, web events, sensor measurements and transaction records.

## 4. Practical example: CSV to Parquet with Python

Use the e-commerce orders dataset below. The example creates a CSV file, reads it using Pandas and writes a Parquet file.

### Sample dataset

| order_id | customer | city | amount |
|---:|---|---|---:|
| 101 | Ananya | Bengaluru | 1200 |
| 102 | Rahul | Mysuru | 800 |
| 103 | Priya | Bengaluru | 1500 |
| 104 | Ananya | Bengaluru | 700 |

### Step 1 — Install the libraries

```bash
pip install pandas pyarrow
```

`pandas` handles the table, while `pyarrow` provides Parquet support.

### Step 2 — Create and save the sample data

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104],
    "customer": ["Ananya", "Rahul", "Priya", "Ananya"],
    "city": ["Bengaluru", "Mysuru", "Bengaluru", "Bengaluru"],
    "amount": [1200, 800, 1500, 700]
})

orders.to_csv("orders.csv", index=False)
print(orders)
```

### Step 3 — Convert CSV to Parquet

```python
orders.to_parquet(
    "orders.parquet",
    index=False,
    engine="pyarrow"
)
```

The resulting `orders.parquet` file stores the data in Parquet format, including schema information.

### Step 4 — Read the Parquet file

```python
parquet_orders = pd.read_parquet(
    "orders.parquet",
    engine="pyarrow"
)

print(parquet_orders)
```

### Step 5 — Perform a simple analysis

```python
print(
    parquet_orders.groupby("city")["amount"]
    .sum()
    .sort_values(ascending=False)
)
```

Expected result:

```text
city
Bengaluru    3400
Mysuru        800
Name: amount, dtype: int64
```

The example demonstrates creating a Parquet file, reading it back and analyzing the stored data.

**Note:** With only four rows, this example demonstrates functionality rather than a meaningful performance improvement. Parquet's advantages are more apparent with larger datasets and analytical workloads.

## 5. Querying only selected columns

Pandas can load only selected columns from a Parquet file:

```python
amounts = pd.read_parquet(
    "orders.parquet",
    columns=["city", "amount"]
)

print(amounts)
```

This avoids loading the `order_id` and `customer` columns into the resulting DataFrame. The Parquet reader can use the file's columnar layout to read only the requested columns.

For SQL-based analytics, tools such as DuckDB can query Parquet files directly:

```sql
SELECT
    city,
    SUM(amount) AS total_sales
FROM read_parquet('orders.parquet')
GROUP BY city
ORDER BY total_sales DESC;
```

This example uses DuckDB SQL; it is not a query that should be run directly in every SQL database.

## 6. CSV versus Parquet

| Feature | CSV | Parquet |
|---|---|---|
| Storage layout | Text, row-oriented representation | Columnar binary format |
| Human readability | Easy to inspect | Not intended for direct text reading |
| Data types | Usually inferred or specified when reading | Schema and types are stored |
| Compression | Possible with separate compression, such as `.csv.gz` | Supports column-level encoding and compression |
| Read selected columns | Often requires parsing rows and fields | Can read only selected columns |
| Typical use | Simple exchange, exports and small files | Analytics, data lakes and larger datasets |
| Editing | Easy to edit in a text editor | Usually written or transformed through software |

Neither format is universally better. CSV is convenient for simple data exchange, while Parquet is usually a stronger choice for repeated analytical queries over structured datasets.

## 7. When should you use Parquet?

Use Parquet when:

- You store large datasets for analysis.
- Queries commonly select a subset of columns.
- Storage and data-scan costs matter.
- You use tools such as Spark, DuckDB, Pandas or cloud analytics engines.
- You want typed, interoperable data files.

CSV may be more convenient when:

- People need to inspect or edit the data manually.
- You are exchanging small, simple tables.
- A receiving system specifically requires CSV.

## 8. What Parquet does not provide by itself

Parquet is a **file format**, not a full data-management platform.

By itself, it does not provide:

- A transaction log for coordinating table updates.
- Full ACID table transactions.
- A complete mechanism for managing concurrent writers.
- A table history or time-travel system.
- A complete orchestration or data-quality pipeline.

Technologies such as **Delta Lake** add table-management capabilities on top of data files, commonly Parquet, using a transaction log and related metadata.

## 9. Student activity

Using the `customers.csv`, `orders.csv` and `products.csv` datasets:

1. Load each CSV file into a Pandas DataFrame.
2. Write each DataFrame to a corresponding Parquet file.
3. Read the Parquet files back and verify row counts and column types.
4. Select only two columns from `orders.parquet`.
5. Calculate total order amount by customer or city.
6. Compare the file sizes of CSV and Parquet.
7. Explain why file-size and speed comparisons on a small dataset may not represent production performance.

### Discussion questions

- Why can Parquet be faster than CSV for some analytical queries?
- What is column pruning?
- Why does Parquet store schema information?
- Does Parquet guarantee that every file will be smaller than its CSV equivalent?
- What additional capabilities does Delta Lake provide beyond Parquet?

## 10. Summary

- **Parquet is a column-oriented file format** optimized for analytical data processing.
- Column pruning can reduce how much data a query needs to read.
- Encoding and compression can reduce storage requirements.
- Parquet preserves schema information and is supported by many tools.
- It is useful in data lakes, analytics pipelines and large datasets.
- Parquet alone is not a transactional table-management system; Delta Lake and similar technologies add those capabilities.
