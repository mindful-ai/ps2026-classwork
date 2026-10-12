# Phase 2 — Data Quality & Trust

Phase 2 extends Phase 1 without changing the project architecture.

## Checks implemented

1. File existence
2. Required columns / schema
3. Required-field null rules
4. Primary-key uniqueness
5. Numeric business rules
6. Valid order dates
7. Referential integrity
8. Raw-to-processed reconciliation
9. JSON data-quality report

## Run

    python src/validate.py

The pipeline returns:

- exit code 0 when all checks pass
- exit code 1 when any check fails

Report:

    reports/data_quality_report.json

## Demonstration exercise

Students can deliberately edit a copy of `orders.csv` and introduce:

- a duplicate `order_id`
- a blank `customer_id`
- quantity = -1
- discount_pct = 150
- an unknown product_id

Then run validation and inspect the failed checks.

Restore the file and rerun. The report should return to PASS.

## Testing

    pytest src/test_validation.py -v
