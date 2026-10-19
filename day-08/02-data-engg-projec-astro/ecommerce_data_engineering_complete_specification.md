# E-Commerce Data Engineering Project --- Complete Specification

**Project type:** End-to-end local data engineering pipeline\
**Project scope:** Exactly six phases\
**Primary outcome:** Transform existing e-commerce CSV files into
validated analytical tables and a machine-learning-ready customer
dataset.\
**Technology stack:** Python, Pandas, DuckDB, PyArrow, Parquet, SQL,
pytest, and JSON reports.

## 1. Project Overview

Build one continuous e-commerce data engineering project that
demonstrates source ingestion, quality controls, storage formats,
analytical transformations, production practices, and the hand-off to
machine learning.

The project must contain **exactly six phases**:

1.  Data & SQL Foundations
2.  Data Quality & Trust
3.  Storage & Formats
4.  Medallion Pipeline (Bronze → Silver → Gold)
5.  Production Practices
6.  ML-Ready Dataset

Do not introduce extra phases, modules, or top-level steps. Streaming,
Delta Lake, cloud platforms, and model training may be discussed as
context, but they are not additional phases or required services.

### Objectives

-   Preserve original transaction data and relationships.
-   Use deterministic mappings to make customer and product descriptions
    realistic without regenerating transactions.
-   Demonstrate joins, CTEs, aggregations, and window functions in SQL.
-   Enforce schema, null, key, domain, date, referential-integrity, and
    reconciliation rules.
-   Demonstrate CSV-to-Parquet conversion, compression, partitioning,
    and schema evolution.
-   Build Bronze, Silver, and Gold data layers.
-   Support safe reruns, quality gates, run reports, and failure
    diagnosis.
-   Produce a documented, validated ML-ready customer feature dataset.

## 2. Technology and Environment

  -----------------------------------------------------------------------
  Technology                          Responsibility
  ----------------------------------- -----------------------------------
  Python                              Pipeline orchestration and
                                      transformations

  Pandas                              DataFrame processing, inspection,
                                      and exports

  DuckDB                              Local analytical SQL engine; reads
                                      CSV and Parquet without a server

  PyArrow                             Parquet storage operations

  Parquet                             Compressed columnar data format

  SQL                                 Joins, CTEs, aggregations, window
                                      functions, and analytical queries

  pytest                              Automated tests

  JSON                                Quality, storage, pipeline, and ML
                                      reports
  -----------------------------------------------------------------------

Use a Python environment compatible with the project's dependencies.
Typical setup:

``` bash
python -m venv .venv
```

Windows activation:

``` bat
.venv\\Scripts\\activate
```

macOS/Linux activation:

``` bash
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

## 3. Source Data Specification

Expected inputs:

``` text
data/
├── raw/
│   ├── orders.csv
│   ├── customers.csv
│   └── products.csv
└── mappings/
    ├── customer_mapping.csv
    └── product_mapping.csv
```

The pipeline consumes the existing CSV files. It must fail clearly when
required files are absent rather than inventing transaction data.

### `customers.csv`

  Column             Meaning
  ------------------ -----------------------------------------
  `customer_id`      Stable customer identifier; primary key
  `customer_name`    Customer display name
  `segment`          Customer segment
  `region`           Business region
  `city`             Customer city
  `customer_since`   Registration/start date

### `products.csv`

  Column               Meaning
  -------------------- ----------------------------------------
  `product_id`         Stable product identifier; primary key
  `product_name`       Product description
  `product_category`   Product category
  `brand`              Product brand
  `cost_price`         Product cost price

### `orders.csv`

  Column              Meaning
  ------------------- ----------------------------------------------
  `order_id`          Order identifier
  `order_date`        Order date
  `customer_id`       Reference to customers
  `product_id`        Reference to products
  `quantity`          Units on the order line
  `unit_price`        Selling price per unit before discount
  `discount_pct`      Discount percentage, 0--100
  `shipping_cost`     Shipping cost associated with the order/line
  `shipping_days`     Shipping duration in days
  `payment_method`    Payment method category
  `customer_rating`   Customer rating, when supplied

**Grain must be verified from the actual source.** The intended grain is
one row per order-product line. If an order has multiple product lines,
`order_id` alone is not unique. Use a genuine line identifier or a
documented composite key such as `order_id + product_id` only when that
combination is guaranteed unique. Never deduplicate legitimate order
lines solely because their order IDs repeat.

### Mapping requirements

-   Preserve customer, product, and order identifiers.
-   Preserve dates, quantities, prices, discounts, and transaction
    relationships.
-   Use deterministic mappings so the same ID always maps to the same
    description.
-   Keep mappings separate from raw source files.
-   Do not regenerate transactions or randomly change financial values.
-   Report unmapped IDs; do not silently drop records.
-   Never overwrite raw source CSV files.

## 4. Data Model and Business Rules

Relationships:

``` text
customers (1) ─────< orders >───── (1) products
```

-   `customers.customer_id` is a primary key.
-   `products.product_id` is a primary key.
-   Orders reference customer and product keys.
-   The order-line key must match the verified source grain.

Minimum business rules:

-   Required identifiers must not be null.
-   Quantity must be greater than zero.
-   Unit price must be non-negative.
-   Discount percentage must be between 0 and 100 inclusive.
-   Dates must parse successfully.
-   Customer and product references must resolve.
-   Dimension keys must be unique.
-   Monetary calculations must use documented rounding and definitions.

Silver-layer calculations:

``` text
gross_amount     = quantity × unit_price
discount_amount  = gross_amount × discount_pct / 100
net_amount       = gross_amount − discount_amount
```

Keep shipping cost separate unless the business definition explicitly
includes it in net sales.

## 5. Target Repository Layout

``` text
ecommerce-data-engineering/
├── README.md
├── requirements.txt
├── run_phase1.bat
├── run_phase2.bat
├── run_phase5.bat
├── run_phase6.bat
├── PHASE5.md
├── PHASE6.md
├── data/
│   ├── raw/
│   ├── mappings/
│   ├── phase1/
│   ├── parquet/
│   ├── partitioned_orders/
│   ├── schema_evolution/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── production/
│   │   ├── staging/
│   │   └── failed/
│   └── ml_ready/
├── sql/
│   ├── phase1_queries.sql
│   ├── phase3_parquet.sql
│   ├── phase4_transformations.sql
│   ├── phase5_production_checks.sql
│   └── phase6_ml_ready.sql
├── src/
│   ├── apply_mappings.py
│   ├── run_sql.py
│   ├── validate.py
│   ├── test_validation.py
│   ├── phase3_storage.py
│   ├── read_parquet_demo.py
│   ├── pipeline.py
│   ├── inspect_gold.py
│   ├── production_pipeline.py
│   ├── test_phase5.py
│   ├── build_ml_ready.py
│   ├── inspect_ml_ready.py
│   └── test_phase6.py
└── reports/
    ├── data_quality_report.json
    ├── storage_report.json
    ├── pipeline_report.json
    ├── runs/
    └── ml/
        └── ml_ready_report.json
```

This is the logical target layout. Generated directories can be empty
before their phase runs. Raw CSV files are inputs, not generated
substitutes.

## 6. Phase Specifications

## Phase 1 --- Data & SQL Foundations

**Objective:** Inspect the source data, establish grain and
relationships, apply deterministic descriptive mappings, and demonstrate
analytical SQL.

**Required implementation:**

1.  Verify all raw files exist.
2.  Inspect schemas, row counts, sample records, and data types.
3.  Apply customer and product mappings.
4.  Preserve identifiers and transaction relationships.
5.  Write mapped outputs to `data/phase1/`.
6.  Query mapped data with DuckDB.
7.  Provide executable SQL examples.

**SQL topics:** basic selection/filtering/sorting; inner and left joins;
`GROUP BY`; CTEs; `ROW_NUMBER`, `RANK`, and `LAG`; revenue summaries by
product, customer, and business dimensions.

**Deliverables:** `src/apply_mappings.py`, `src/run_sql.py`,
`sql/phase1_queries.sql`, mapped CSV outputs, phase notes, and run
instructions.

**Acceptance:** mappings are repeatable; IDs and relationships are
preserved; before/after row counts are reported; SQL examples run
successfully.

## Phase 2 --- Data Quality & Trust

**Objective:** Make data quality rules executable, visible, and
repeatable.

**Required checks:**

1.  Required files exist.
2.  Required columns are present.
3.  Required fields satisfy null rules.
4.  Dimension keys and the verified order-line key are unique.
5.  Numeric business rules pass.
6.  Dates parse.
7.  Customer and product foreign keys resolve.
8.  Raw-to-mapped row counts reconcile when mapping should not change
    row counts.
9.  A JSON quality report is written.

**Deliverables:** `src/validate.py`, `src/test_validation.py`,
`reports/data_quality_report.json`, phase notes, and instructions for
introducing/fixing invalid rows.

**Failure behaviour:** report failed checks; return a non-zero exit
code; never silently discard invalid rows to make validation pass.
Demonstrate both PASS and FAIL using examples such as a missing customer
ID, invalid quantity, invalid discount, duplicate key, or unknown
product ID.

## Phase 3 --- Storage & Formats

**Objective:** Demonstrate columnar storage, compression, partitioning,
and schema evolution.

**Required implementation:**

1.  Convert mapped customers, products, and orders from CSV to Parquet.
2.  Use Snappy compression where supported.
3.  Compare CSV and Parquet sizes and calculate percentage reduction.
4.  Read Parquet with Pandas/PyArrow.
5.  Query Parquet directly with DuckDB.
6.  Partition orders by year and month.
7.  Demonstrate schema evolution by adding a column in a later schema
    version.

**Expected outputs:**

``` text
data/parquet/{customers,products,orders}.parquet
data/partitioned_orders/...
data/schema_evolution/...
reports/storage_report.json
```

The storage report records file sizes, row counts, size reduction,
partition details, and schema evolution details.

Explain CSV versus Parquet, compression, partition pruning, and schema
compatibility. Delta Lake may be explained conceptually as Parquet data
files plus a transaction log and features such as ACID transactions,
schema enforcement/evolution, and time travel. Delta Lake is not a
separate phase or required dependency.

**Acceptance:** CSV and Parquet row counts reconcile; Parquet can be
queried; partitioned data can be queried; the schema evolution example
demonstrates an added column.

## Phase 4 --- Medallion Pipeline (Bronze → Silver → Gold)

**Objective:** Build a local transformation pipeline from mapped inputs
to preserved, cleaned, and analytical layers.

### Bronze

``` text
data/bronze/
├── orders.parquet
├── customers.parquet
└── products.parquet
```

Preserve the mapped source structure in Parquet. Avoid business
transformations beyond consistent ingestion. Never modify raw CSV files.

### Silver

``` text
data/silver/
├── orders.parquet
├── customers.parquet
└── products.parquet
```

Standardize dates and data types; apply documented deduplication using
the actual grain; enforce rules; derive `gross_amount`,
`discount_amount`, and `net_amount`; retain useful source columns and
relationships. Never deduplicate by `order_id` alone if it removes valid
order lines.

### Gold

``` text
data/gold/
├── enriched_orders.parquet
├── sales_summary.parquet
└── customer_features.parquet
```

-   `enriched_orders.parquet`: order facts joined to customer and
    product attributes.
-   `sales_summary.parquet`: aggregate by relevant dimensions such as
    date, region, and product category; include order count, units,
    gross sales, discount amount, and net sales.
-   `customer_features.parquet`: one row per customer with total orders,
    units, spend, average order value, average discount, average rating
    where available, first/last order dates, and favorite category where
    determinable.

**Deliverables:** `src/pipeline.py`, `src/inspect_gold.py`,
`sql/phase4_transformations.sql`, `reports/pipeline_report.json`, and
phase documentation.

**Acceptance:** Bronze/Silver/Gold outputs exist; keys resolve;
financial calculations follow documented rules; Gold grains are
explicit; row counts and status are reported.

## Phase 5 --- Production Practices

**Objective:** Make the pipeline safely repeatable, observable, and
diagnosable.

**Required capabilities:**

1.  Quality gates before output promotion.
2.  Bronze/Silver reconciliation where row counts should match.
3.  Fresh staging directory for each run.
4.  Verification of staged files before promotion.
5.  Full rebuild rather than appending to existing Gold tables.
6.  Run ID and start/completion timestamps.
7.  Input fingerprints, row counts, quality results, and final status in
    reports.
8.  Error details for failed runs.
9.  Exit code 0 on success and non-zero on failure.
10. Tests proving repeated runs do not accumulate duplicate rows.

Runtime layout:

``` text
data/production/
├── staging/
└── failed/
reports/runs/<run_id>.json
```

Use SHA-256 or equivalent to fingerprint inputs. Record which inputs
were used; a fingerprint is audit metadata, not a correctness guarantee.

Each report should contain run ID, pipeline name, timestamps, input
fingerprints, quality-gate results, relevant row counts, status
(`SUCCESS`/`FAILED`), and error/traceback on failure.

Failures must stop promotion and retain useful diagnostics. Promotion of
several files is not inherently one atomic filesystem transaction;
document this limitation. A stronger design can promote a versioned
output directory and update one current-version pointer.

**Deliverables:** `src/production_pipeline.py`, `src/test_phase5.py`,
`sql/phase5_production_checks.sql`, run reports, `run_phase5.bat`, and
documentation.

**Acceptance:** successful runs create reports; invalid data fails the
quality gate; failed runs return non-zero; repeated runs do not increase
row counts; raw data stays unchanged; a corrected rerun succeeds.

## Phase 6 --- ML-Ready Dataset

**Objective:** Produce a clean, documented feature table from Gold. This
is the final phase.

**Input:** `data/gold/customer_features.parquet`

**Outputs:**

``` text
data/ml_ready/
├── customer_ml_ready.parquet
├── customer_ml_ready.csv
└── feature_dictionary.json
reports/ml/ml_ready_report.json
```

**Required transformations:**

1.  Load the Gold customer feature table.
2.  Validate required source columns.
3.  Derive customer tenure in days from first/last order dates.
4.  Derive recency relative to a documented reference date, such as the
    latest date in the dataset.
5.  Encode categorical columns such as segment, region, and favorite
    category.
6.  Keep `customer_id` as an identifier, not a model feature.
7.  Exclude raw names and raw dates from the numeric training matrix.
8.  Handle missing values using a documented policy.
9.  Validate the final dataset.
10. Export Parquet and CSV.
11. Write a feature dictionary and build report.

Expected feature groups include activity (`total_orders`,
`total_units`), monetary (`total_spend`, `average_order_value`),
behaviour (`average_discount`, `average_rating`), lifecycle
(`customer_tenure_days`, `recency_days`), and encoded categories. The
actual one-hot columns depend on the data; the dictionary must describe
the columns actually generated.

**Validation:** dataset is non-empty; customer IDs are unique; no
missing values remain under the chosen policy; all features except
`customer_id` are numeric; spend is non-negative; included customers
have positive orders and units; the feature dictionary covers the output
columns.

**Deliverables:** `src/build_ml_ready.py`, `src/inspect_ml_ready.py`,
`src/test_phase6.py`, `sql/phase6_ml_ready.sql`, Parquet/CSV exports,
feature dictionary, ML report, and phase documentation.

Example hand-off:

``` python
import pandas as pd

df = pd.read_parquet("data/ml_ready/customer_ml_ready.parquet")
customer_ids = df["customer_id"]  # retain for traceability
X = df.drop(columns=["customer_id"])
```

This project ends at the ML-ready data hand-off. Train/validation/test
splitting, scaling, training, evaluation, and deployment are downstream
ML activities, not extra phases.

## 7. End-to-End Execution Order

Run phases in sequence because later phases depend on earlier outputs.
Typical commands from the project root:

``` bash
python src/apply_mappings.py
python src/run_sql.py

python src/validate.py
pytest -q src/test_validation.py

python src/phase3_storage.py
python src/read_parquet_demo.py

python src/pipeline.py
python src/inspect_gold.py

python src/production_pipeline.py
pytest -q src/test_phase5.py

python src/build_ml_ready.py
python src/inspect_ml_ready.py
pytest -q src/test_phase6.py
```

Use the actual command names in the delivered repository if they differ.
The source CSVs and required prior-phase outputs must exist before
dependent commands run.

## 8. Cross-Cutting Requirements

### Reproducibility

-   Mappings are deterministic.
-   Transformations and data grains are documented.
-   Reports identify inputs and status.
-   Re-running unchanged inputs must not append duplicates.

### Data protection

-   Never overwrite raw inputs.
-   Never silently discard invalid rows.
-   Preserve failure diagnostics.
-   Do not put credentials or secrets in code or reports.

### Logging and testing

Each stage should emit clear console messages and the specified
machine-readable report. Tests should cover schema, null/domain rules,
key uniqueness, referential integrity, reconciliation, ML feature
types/missing values, and production repeatability. Tests must not pass
simply because required output files are missing; document prerequisites
or use fixtures for isolated logic tests.

### Documentation

Each phase documents its purpose, inputs, outputs, transformations,
commands, reports, failure scenarios, and acceptance criteria.

## 9. Performance and Design Boundaries

This is a local educational implementation, not a claim of
enterprise-scale readiness.

-   Pandas is suitable for the supplied dataset size.
-   DuckDB provides SQL analytics without a server.
-   Partition by useful query fields such as order year/month without
    creating excessive tiny files.
-   Streaming is discussed conceptually; a streaming service is not
    required.
-   Delta Lake is discussed conceptually; its transaction engine is not
    required.
-   Cloud orchestration and centralized observability are out of scope.
-   Model training is outside the final deliverable.

## 10. Definition of Done

The project is complete when all six phases have executable code and
documentation, and the supplied CSVs can be processed to produce:

-   Deterministically mapped Phase 1 data
-   Phase 2 quality reports and passing/failing examples
-   Parquet conversions, storage report, partitions, and
    schema-evolution example
-   Bronze, Silver, and Gold Parquet tables
-   Production run reports, quality gates, and repeatability
    verification
-   ML-ready Parquet and CSV exports
-   Feature dictionary and ML-ready validation report
-   Automated tests for key data contracts

Final data flow:

``` text
Existing CSV sources
        |
        v
PHASE 1 — Data & SQL Foundations
        |
        v
PHASE 2 — Data Quality & Trust
        |
        v
PHASE 3 — Storage & Formats
        |
        v
PHASE 4 — Bronze → Silver → Gold
        |
        v
PHASE 5 — Production Practices
        |
        v
PHASE 6 — ML-Ready Dataset
        |
        v
data/ml_ready/customer_ml_ready.parquet
```

**Final outcome:** a documented, locally executable e-commerce data
engineering pipeline that transforms existing CSV data through
validation, efficient storage, medallion processing, production-style
controls, and an ML-ready customer feature dataset---within exactly six
phases.
