# Phase 3 — Storage & Formats

Phase 3 extends the same project after Phase 2 validation.

## Objectives

- Convert CSV data to Parquet.
- Demonstrate columnar storage.
- Compare CSV and Parquet file sizes.
- Use Snappy compression.
- Query Parquet directly with DuckDB.
- Partition orders by year and month.
- Demonstrate schema evolution using versioned Parquet datasets.

## Run

First ensure Phase 1 mapped files exist:

    python src/apply_mappings.py

Then run Phase 2 validation:

    python src/validate.py

Then run Phase 3:

    python src/phase3_storage.py

## Outputs

data/parquet/
    customers.parquet
    products.parquet
    orders.parquet

data/partitioned_orders/
    order_year=YYYY/
        order_month=MM/
            *.parquet

data/schema_evolution/
    customer_features_v1.parquet
    customer_features_v2.parquet

reports/storage_report.json

## Direct Parquet reading

    python src/read_parquet_demo.py

## DuckDB

The SQL examples in `sql/phase3_parquet.sql` demonstrate that DuckDB
can query Parquet directly.

## Teaching demonstrations

### Compression

Compare CSV bytes with Snappy-compressed Parquet bytes.

### Partitioning

Orders are partitioned by:

    order_year
    order_month

A query filtering by year/month can avoid irrelevant partitions in a
partition-aware analytical engine.

### Schema evolution

Version 1:

    customer_id
    customer_segment

Version 2:

    customer_id
    customer_segment
    customer_region

The demonstration shows how a dataset can gain columns while preserving
the existing fields.

## Delta concept

This phase introduces the concepts behind Delta Lake:

- Parquet files as the physical storage layer.
- A transaction log as the coordination/metadata layer.
- Schema enforcement/evolution.
- ACID-style table operations.
- Time travel.

Delta Lake implementation itself is intentionally kept conceptual here;
the hands-on implementation remains Python + PyArrow + Parquet + DuckDB.
