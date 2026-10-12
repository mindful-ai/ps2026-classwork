# E-commerce Data Engineering — Phase 4

Phase 4 implements the actual Bronze → Silver → Gold pipeline.

Sequence:

Phase 1: Data & SQL Foundations
Phase 2: Data Quality & Trust
Phase 3: Storage & Formats
Phase 4: Medallion Pipeline

Run:

    python src/pipeline.py

Main outputs:

    data/bronze/
    data/silver/
    data/gold/

Gold includes:

    enriched_orders.parquet
    sales_summary.parquet
    customer_features.parquet
