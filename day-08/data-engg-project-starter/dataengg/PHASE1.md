# E-commerce Data Engineering — Phase 1

Phase 1 uses the existing `orders.csv`, `customers.csv`, and `products.csv`
as the source data. IDs and transaction relationships are preserved.

## Phase 1 scope

- Realistic customer/product mapping
- Keys and relationships
- Data grain
- DuckDB SQL exploration
- Joins
- Aggregations
- CTEs
- Window functions

## Input files

Copy the previously developed files here:

    data/raw/orders.csv
    data/raw/customers.csv
    data/raw/products.csv

## Install

    pip install -r requirements.txt

## Run mapping

    python src/apply_mappings.py

This creates:

    data/phase1/customers_mapped.csv
    data/phase1/products_mapped.csv
    data/phase1/orders_mapped.csv

The original IDs remain unchanged.

## Run SQL examples

    python src/run_sql.py

The SQL is executed against the mapped CSV files using DuckDB.

## Important

The mapping is deterministic. If the same input files are used again,
the same customer/product names are assigned to the same IDs.
