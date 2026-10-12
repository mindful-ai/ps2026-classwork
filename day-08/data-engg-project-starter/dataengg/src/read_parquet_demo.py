
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "parquet"

def main():
    orders = PARQUET / "orders.parquet"

    print("=== Full Parquet schema ===")
    print(pq.read_schema(orders))

    print("\n=== Read selected columns ===")
    df = pd.read_parquet(
        orders,
        columns=["order_id", "customer_id", "product_id", "quantity", "unit_price"]
    )
    print(df.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
