# Phase 5 — Production Practices

This phase upgrades the Bronze → Silver → Gold pipeline into a repeatable production-style pipeline.

## Scope

- safe reruns
- idempotent output generation
- quality gates
- reconciliation
- staging before promotion
- failure isolation
- run metadata and audit reports
- repeatability tests

## Flow

```text
Bronze → Quality Gate → Build Gold in staging → Verify → Promote → Audit
                         └─ failure → failed/<run_id>/
```

## Run

Complete Phase 4 first, then:

```bash
python src/production_pipeline.py
```

Success returns exit code `0`; failure returns `1`.

## Quality gate

Checks required files, non-empty tables, key uniqueness, required order values, foreign keys, and Bronze/Silver row-count reconciliation. Gold is not promoted when the gate fails.

## Safe reruns

Gold is rebuilt into a fresh staging directory and verified before promotion. The pipeline does not append to existing Gold tables, so running it twice does not accumulate duplicate rows.

## Run audit

Each run writes:

```text
reports/runs/<run_id>.json
```

It records timestamps, input SHA-256 fingerprints, quality-gate results, output row counts, and failure information.

## Failure handling

Failed staging output is retained under:

```text
data/production/failed/<run_id>/
```

This makes the failed run inspectable without changing the raw source data.

## Tests

```bash
pytest -q src/test_phase5.py
```

The repeatability test runs the production pipeline twice and verifies that the Gold row count remains unchanged.

## Exercise

1. Run Phase 4.
2. Run Phase 5.
3. Run Phase 5 again.
4. Compare Gold row counts.
5. Inspect `reports/runs/`.
6. Introduce an invalid foreign key into Silver.
7. Run Phase 5 and observe the quality-gate failure.
8. Restore the data and rerun successfully.

**Key lesson:** a production data pipeline must be validated, rerunnable, auditable, and recoverable—not just capable of transforming data.
