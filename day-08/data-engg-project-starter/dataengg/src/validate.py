
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase1"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

FILES = {
    "customers": DATA / "customers_mapped.csv",
    "products": DATA / "products_mapped.csv",
    "orders": DATA / "orders_mapped.csv",
}

EXPECTED = {
    "customers": {
        "required": ["customer_id", "customer_name"],
        "unique": ["customer_id"],
        "not_null": ["customer_id", "customer_name"],
    },
    "products": {
        "required": ["product_id", "product_name"],
        "unique": ["product_id"],
        "not_null": ["product_id", "product_name"],
    },
    "orders": {
        "required": [
            "order_id", "order_date", "customer_id", "product_id",
            "quantity", "unit_price", "discount_pct",
        ],
        "unique": ["order_id"],
        "not_null": [
            "order_id", "order_date", "customer_id", "product_id",
            "quantity", "unit_price",
        ],
    },
}

def check_schema(df, required):
    missing = [c for c in required if c not in df.columns]
    return {"pass": not missing, "missing_columns": missing}

def check_not_null(df, columns):
    result = {}
    passed = True
    for col in columns:
        nulls = int(df[col].isna().sum())
        result[col] = nulls
        if nulls:
            passed = False
    return {"pass": passed, "null_counts": result}

def check_unique(df, columns):
    result = {}
    passed = True
    for col in columns:
        duplicates = int(df[col].duplicated(keep=False).sum())
        result[col] = duplicates
        if duplicates:
            passed = False
    return {"pass": passed, "duplicate_value_rows": result}

def main():
    report = {"phase": 2, "checks": {}, "status": "PASS"}

    frames = {}
    for name, path in FILES.items():
        check = {"file_exists": path.exists(), "rows": None}
        if not path.exists():
            check["pass"] = False
            report["checks"][name] = check
            report["status"] = "FAIL"
            continue

        df = pd.read_csv(path)
        frames[name] = df
        check["rows"] = len(df)

        schema = check_schema(df, EXPECTED[name]["required"])
        nulls = check_not_null(df, EXPECTED[name]["not_null"])
        unique = check_unique(df, EXPECTED[name]["unique"])

        check.update({
            "schema": schema,
            "not_null": nulls,
            "unique": unique,
            "pass": schema["pass"] and nulls["pass"] and unique["pass"],
        })
        report["checks"][name] = check

        if not check["pass"]:
            report["status"] = "FAIL"

    # Orders business rules
    if "orders" in frames:
        o = frames["orders"].copy()
        numeric_rules = {
            "quantity_gt_zero": int((pd.to_numeric(o["quantity"], errors="coerce") <= 0).sum()),
            "unit_price_non_negative": int((pd.to_numeric(o["unit_price"], errors="coerce") < 0).sum()),
            "discount_between_0_and_100": int((
                (pd.to_numeric(o["discount_pct"], errors="coerce") < 0) |
                (pd.to_numeric(o["discount_pct"], errors="coerce") > 100)
            ).sum()),
        }
        passed = all(v == 0 for v in numeric_rules.values())
        report["checks"]["orders_business_rules"] = {
            "pass": passed,
            "violations": numeric_rules,
        }
        if not passed:
            report["status"] = "FAIL"

        parsed_dates = pd.to_datetime(o["order_date"], errors="coerce")
        invalid_dates = int(parsed_dates.isna().sum())
        report["checks"]["order_date_valid"] = {
            "pass": invalid_dates == 0,
            "invalid_dates": invalid_dates,
        }
        if invalid_dates:
            report["status"] = "FAIL"

    # Referential integrity
    if {"orders", "customers", "products"} <= frames.keys():
        o = frames["orders"]
        c = set(frames["customers"]["customer_id"].astype(str))
        p = set(frames["products"]["product_id"].astype(str))

        orphan_customers = int((~o["customer_id"].astype(str).isin(c)).sum())
        orphan_products = int((~o["product_id"].astype(str).isin(p)).sum())

        passed = orphan_customers == 0 and orphan_products == 0
        report["checks"]["referential_integrity"] = {
            "pass": passed,
            "orphan_customer_rows": orphan_customers,
            "orphan_product_rows": orphan_products,
        }
        if not passed:
            report["status"] = "FAIL"

    # Reconciliation: source Phase 1 files vs current files.
    # Since Phase 1 mappings preserve rows, counts should match the raw inputs.
    raw = ROOT / "data" / "raw"
    reconciliation = {}
    recon_pass = True
    for name in FILES:
        raw_file = raw / f"{name}.csv"
        phase_file = FILES[name]
        if raw_file.exists() and phase_file.exists():
            raw_rows = len(pd.read_csv(raw_file))
            phase_rows = len(pd.read_csv(phase_file))
            ok = raw_rows == phase_rows
            reconciliation[name] = {
                "raw_rows": raw_rows,
                "phase1_rows": phase_rows,
                "difference": phase_rows - raw_rows,
                "pass": ok,
            }
            recon_pass = recon_pass and ok

    report["checks"]["reconciliation"] = {
        "pass": recon_pass,
        "tables": reconciliation,
    }
    if not recon_pass:
        report["status"] = "FAIL"

    # Summary
    total = 0
    passed = 0
    for key, value in report["checks"].items():
        if isinstance(value, dict) and "pass" in value:
            total += 1
            passed += int(value["pass"])

    report["summary"] = {
        "checks_evaluated": total,
        "checks_passed": passed,
        "checks_failed": total - passed,
    }

    out = REPORTS / "data_quality_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 60)
    print("PHASE 2 — DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Status: {report['status']}")
    print(f"Checks: {passed}/{total} passed")
    print(f"Report: {out}")

    if report["status"] != "PASS":
        print("\nFAILED CHECKS:")
        for name, value in report["checks"].items():
            if isinstance(value, dict) and value.get("pass") is False:
                print(f"  - {name}")

    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
