
from pathlib import Path
import json
import shutil
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "phase1"
PARQUET = ROOT / "data" / "parquet"
PARTITIONED = ROOT / "data" / "partitioned_orders"
EVOLUTION = ROOT / "data" / "schema_evolution"
REPORTS = ROOT / "reports"

PARQUET.mkdir(parents=True, exist_ok=True)
PARTITIONED.mkdir(parents=True, exist_ok=True)
EVOLUTION.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

TABLES = {
    "customers": SOURCE / "customers_mapped.csv",
    "products": SOURCE / "products_mapped.csv",
    "orders": SOURCE / "orders_mapped.csv",
}

def require_inputs():
    missing = [str(p) for p in TABLES.values() if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing Phase 1 mapped files. Run `python src/apply_mappings.py` first. "
            + ", ".join(missing)
        )

def write_parquet_tables():
    results = {}
    for name, path in TABLES.items():
        df = pd.read_csv(path)
        out = PARQUET / f"{name}.parquet"

        # Explicitly use Parquet compression.
        df.to_parquet(out, engine="pyarrow", compression="snappy", index=False)

        results[name] = {
            "csv_bytes": path.stat().st_size,
            "parquet_bytes": out.stat().st_size,
            "rows": len(df),
            "columns": list(df.columns),
            "compression": "snappy",
        }
        results[name]["size_reduction_pct"] = round(
            100 * (1 - results[name]["parquet_bytes"] / results[name]["csv_bytes"]), 2
        )

    return results

def create_partitioned_orders():
    df = pd.read_csv(TABLES["orders"])
    if "order_date" not in df.columns:
        raise ValueError("orders.csv must contain order_date")

    dt = pd.to_datetime(df["order_date"], errors="coerce")
    if dt.isna().any():
        raise ValueError("Cannot partition orders: invalid order_date values found.")

    df = df.copy()
    df["order_year"] = dt.dt.year
    df["order_month"] = dt.dt.month

    # Rebuild the demo output so rerunning produces a clean deterministic result.
    if PARTITIONED.exists():
        for item in PARTITIONED.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    table = pa.Table.from_pandas(df, preserve_index=False)

    pq.write_to_dataset(
        table,
        root_path=str(PARTITIONED),
        partition_cols=["order_year", "order_month"],
        compression="snappy",
    )

    partitions = sorted(
        str(p.relative_to(PARTITIONED))
        for p in PARTITIONED.rglob("*.parquet")
    )

    return {
        "partition_columns": ["order_year", "order_month"],
        "partition_count": len(partitions),
        "partitions": partitions[:50],
    }

def schema_evolution_demo():
    # Version 1: base customer features.
    customers = pd.read_csv(TABLES["customers"])
    required = "customer_id"
    if required not in customers.columns:
        raise ValueError("customers.csv must contain customer_id")

    v1 = customers[["customer_id"]].copy()
    v1["customer_segment"] = (
        customers["segment"] if "segment" in customers.columns else "Unknown"
    )
    v1_path = EVOLUTION / "customer_features_v1.parquet"
    v1.to_parquet(v1_path, compression="snappy", index=False)

    # Version 2: evolved schema with a new derived column.
    v2 = v1.copy()
    v2["customer_region"] = (
        customers["region"] if "region" in customers.columns else "Unknown"
    )
    v2_path = EVOLUTION / "customer_features_v2.parquet"
    v2.to_parquet(v2_path, compression="snappy", index=False)

    schema1 = [field.name for field in pq.read_schema(v1_path)]
    schema2 = [field.name for field in pq.read_schema(v2_path)]

    return {
        "v1_columns": schema1,
        "v2_columns": schema2,
        "new_columns": [c for c in schema2 if c not in schema1],
        "backward_columns": [c for c in schema1 if c in schema2],
    }

def main():
    require_inputs()

    compression = write_parquet_tables()
    partitions = create_partitioned_orders()
    evolution = schema_evolution_demo()

    report = {
        "phase": 3,
        "parquet": compression,
        "partitioning": partitions,
        "schema_evolution": evolution,
    }

    report_path = REPORTS / "storage_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 64)
    print("PHASE 3 — STORAGE & FORMATS")
    print("=" * 64)

    print("\nPARQUET")
    for name, r in compression.items():
        print(
            f"{name:10} rows={r['rows']:,}  "
            f"CSV={r['csv_bytes']:,} bytes  "
            f"Parquet={r['parquet_bytes']:,} bytes  "
            f"reduction={r['size_reduction_pct']}%"
        )

    print("\nPARTITIONING")
    print(f"Partition columns: {partitions['partition_columns']}")
    print(f"Partition files  : {partitions['partition_count']}")

    print("\nSCHEMA EVOLUTION")
    print(f"V1: {evolution['v1_columns']}")
    print(f"V2: {evolution['v2_columns']}")
    print(f"New: {evolution['new_columns']}")

    print(f"\nReport: {report_path}")

if __name__ == "__main__":
    main()
