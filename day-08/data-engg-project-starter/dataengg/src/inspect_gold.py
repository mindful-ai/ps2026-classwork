
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "data" / "gold"

con = duckdb.connect()

for name in [
    "enriched_orders.parquet",
    "sales_summary.parquet",
    "customer_features.parquet",
]:
    path = GOLD / name
    print(f"\n=== {name} ===")
    print(con.execute(
        f"SELECT * FROM read_parquet('{path.as_posix()}') LIMIT 10"
    ).fetchdf().to_string(index=False))

con.close()
