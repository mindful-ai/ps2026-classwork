# Industry Data Validation Checklist

Data validation helps ensure that data is accurate, complete, consistent, reliable, and suitable for downstream use in analytics, reporting, and machine learning.

## Important Industry Validations

| # | Validation | What it checks |
|---:|---|---|
| 1 | **Schema validation** | Expected columns, data types, and schema changes |
| 2 | **Completeness** | Required fields are not null or missing |
| 3 | **Uniqueness** | Primary keys and business keys are unique at the correct data grain |
| 4 | **Data type validation** | Values conform to expected types, such as dates, integers, and decimals |
| 5 | **Domain validation** | Values belong to an allowed set, e.g., payment method |
| 6 | **Range validation** | Values fall within acceptable limits, e.g., quantity > 0 |
| 7 | **Format validation** | Dates, email addresses, phone numbers, and identifiers follow expected formats |
| 8 | **Referential integrity** | Foreign keys reference existing records |
| 9 | **Business-rule validation** | Business conditions hold, e.g., discount between 0% and 100% |
| 10 | **Cross-field validation** | Related fields are logically consistent, e.g., delivery date >= order date |
| 11 | **Duplicate detection** | Exact duplicates and potential duplicate business records are identified |
| 12 | **Freshness validation** | Data arrives within the expected time window |
| 13 | **Volume validation** | Row counts and data volumes stay within expected thresholds |
| 14 | **Reconciliation** | Source, transformed, rejected, and target record counts and totals agree |
| 15 | **Statistical/anomaly validation** | Unexpected changes in distributions, averages, null rates, or outliers |
| 16 | **Transformation validation** | Derived columns and calculations produce correct results |
| 17 | **Integrity/checksum validation** | File integrity, transfer completeness, and corruption checks |
| 18 | **Security and privacy validation** | Sensitive data, access rules, masking, and prohibited fields |
| 19 | **Data drift validation** | Changes in feature distributions that may affect downstream ML models |
| 20 | **Pipeline and quality-gate validation** | Failed checks block or quarantine data before production publishing |

## Recommended Starting Point for the E-commerce Project

Prioritize these validations first:

1. Schema validation
2. Completeness
3. Uniqueness at the correct data grain
4. Data type and format validation
5. Range validation
6. Business-rule validation
7. Referential integrity
8. Duplicate detection
9. Reconciliation
10. Quarantine handling

## Industry Practice

Critical validations should be:

- **Automated** so they run consistently in each pipeline execution.
- **Measurable** with counts, percentages, thresholds, and clear pass/fail results.
- **Logged** so failures can be investigated and audited.
- **Enforceable** through quality gates that determine whether data is published, warned on, or blocked.
- **Traceable** so invalid rows can be inspected or quarantined without silently losing data.

A pipeline may use three outcomes:

- **PASS** — all critical checks meet their thresholds.
- **WARN** — a non-critical check exceeds its preferred threshold but processing may continue.
- **FAIL** — a critical check fails and publication is blocked until the issue is resolved.

**Important:** Uniqueness must be evaluated at the correct data grain. For example, `order_id` may repeat when an order contains multiple product lines. Do not classify repeated order IDs as duplicates unless the data model says they must be unique.
