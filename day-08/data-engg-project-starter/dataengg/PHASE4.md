# Phase 4 — Medallion Pipeline

This phase converts the work from Phases 1–3 into a complete local
Bronze → Silver → Gold data pipeline.

## Architecture

Raw CSV
  ↓
Phase 1 mapped data
  ↓
BRONZE — source-aligned Parquet
  ↓
SILVER — typed, deduplicated, derived measures
  ↓
GOLD — analytical and ML-ready datasets

## Run

Make sure the mapped Phase 1 files exist:

    python src/apply_mappings.py

Validate them:

    python src/validate.py

Run the pipeline:

    python src/pipeline.py

## Bronze

Bronze stores the mapped source tables as Parquet:

    data/bronze/
        orders.parquet
        customers.parquet
        products.parquet

## Silver

Silver contains:

- typed order dates
- deduplicated keys
- gross amount
- discount amount
- net amount
- cleaned customer/product tables

Output:

    data/silver/

## Gold

Three analytical outputs are created:

### enriched_orders.parquet

Order-level analytical dataset with customer and product attributes.

### sales_summary.parquet

Aggregated sales by:

- date
- region
- product category

### customer_features.parquet

Customer-level features suitable for the next ML stage.

Examples:

- total_orders
- total_units
- total_spend
- average_order_value
- average_discount
- average_rating
- first_order_date
- last_order_date
- favorite_category

## Idempotent rebuild behavior

The generated Bronze/Silver/Gold layers are rebuilt deterministically.
The raw input files are never modified.

Running:

    python src/pipeline.py

multiple times produces the same logical outputs instead of appending
duplicate records.

The more explicit production-grade idempotency and rerun/failure
controls belong to Phase 5.
