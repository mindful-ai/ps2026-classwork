
from pathlib import Path
import json
import shutil
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"
REPORTS = ROOT / "reports"

MAPPED = ROOT / "data" / "phase1"
PARQUET = ROOT / "data" / "parquet"

for d in [BRONZE, SILVER, GOLD, REPORTS]:
    d.mkdir(parents=True, exist_ok=True)

def clean_output():
    # Deterministic rebuild: remove generated layers, never raw input.
    for d in [BRONZE, SILVER, GOLD]:
        if d.exists():
            for item in d.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

def require_inputs():
    required = [
        MAPPED / "orders_mapped.csv",
        MAPPED / "customers_mapped.csv",
        MAPPED / "products_mapped.csv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing mapped Phase 1 files. Run `python src/apply_mappings.py` first."
        )

def write_bronze():
    paths = {
        "orders": MAPPED / "orders_mapped.csv",
        "customers": MAPPED / "customers_mapped.csv",
        "products": MAPPED / "products_mapped.csv",
    }

    counts = {}
    for name, src in paths.items():
        df = pd.read_csv(src)

        # Bronze: preserve source-level records but store them as Parquet.
        out = BRONZE / f"{name}.parquet"
        df.to_parquet(out, engine="pyarrow", compression="snappy", index=False)
        counts[name] = len(df)

    return counts

def write_silver():
    con = duckdb.connect()
    silver = {}

    # Read Bronze Parquet directly.
    con.execute(f"""
        CREATE OR REPLACE VIEW orders AS
        SELECT * FROM read_parquet('{(BRONZE / "orders.parquet").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW customers AS
        SELECT * FROM read_parquet('{(BRONZE / "customers.parquet").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW products AS
        SELECT * FROM read_parquet('{(BRONZE / "products.parquet").as_posix()}')
    """)

    # Silver orders: typed, deduplicated and with a derived gross amount.
    orders = con.execute("""
        SELECT *
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY order_id
                    ORDER BY order_date
                ) AS _rn
            FROM orders
        )
        WHERE _rn = 1
    """).fetchdf()

    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    )

    # Keep the financial calculation explicit and reproducible.
    orders["gross_amount"] = (
        pd.to_numeric(orders["quantity"], errors="coerce")
        * pd.to_numeric(orders["unit_price"], errors="coerce")
    )

    # Discount amount and net amount.
    if "discount_pct" in orders.columns:
        orders["discount_amount"] = (
            orders["gross_amount"]
            * pd.to_numeric(orders["discount_pct"], errors="coerce").fillna(0)
            / 100.0
        )
        orders["net_amount"] = orders["gross_amount"] - orders["discount_amount"]

    orders = orders.drop(columns=["_rn"], errors="ignore")

    customers = con.execute("""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY customer_id
                       ORDER BY customer_id
                   ) AS _rn
            FROM customers
        )
        WHERE _rn = 1
    """).fetchdf().drop(columns=["_rn"], errors="ignore")

    products = con.execute("""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY product_id
                       ORDER BY product_id
                   ) AS _rn
            FROM products
        )
        WHERE _rn = 1
    """).fetchdf().drop(columns=["_rn"], errors="ignore")

    orders.to_parquet(SILVER / "orders.parquet", compression="snappy", index=False)
    customers.to_parquet(SILVER / "customers.parquet", compression="snappy", index=False)
    products.to_parquet(SILVER / "products.parquet", compression="snappy", index=False)

    silver["orders"] = len(orders)
    silver["customers"] = len(customers)
    silver["products"] = len(products)

    con.close()
    return silver

def write_gold():
    con = duckdb.connect()

    con.execute(f"""
        CREATE OR REPLACE VIEW orders AS
        SELECT * FROM read_parquet('{(SILVER / "orders.parquet").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW customers AS
        SELECT * FROM read_parquet('{(SILVER / "customers.parquet").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW products AS
        SELECT * FROM read_parquet('{(SILVER / "products.parquet").as_posix()}')
    """)

    # Gold 1: enriched order-level analytical dataset.
    enriched = con.execute("""
        SELECT
            o.order_id,
            CAST(o.order_date AS DATE) AS order_date,
            o.customer_id,
            c.customer_name,
            c.segment,
            c.region,
            o.product_id,
            p.product_name,
            p.product_category,
            p.brand,
            o.quantity,
            o.unit_price,
            o.discount_pct,
            o.gross_amount,
            o.discount_amount,
            o.net_amount,
            o.shipping_cost,
            o.shipping_days,
            o.payment_method,
            o.customer_rating
        FROM orders o
        LEFT JOIN customers c
            ON o.customer_id = c.customer_id
        LEFT JOIN products p
            ON o.product_id = p.product_id
    """).fetchdf()

    # Gold 2: sales summary.
    sales = con.execute("""
        SELECT
            CAST(o.order_date AS DATE) AS order_date,
            c.region,
            p.product_category,
            COUNT(DISTINCT o.order_id) AS order_count,
            SUM(o.quantity) AS units,
            SUM(o.gross_amount) AS gross_sales,
            SUM(o.discount_amount) AS discount_amount,
            SUM(o.net_amount) AS net_sales
        FROM orders o
        LEFT JOIN customers c
            ON o.customer_id = c.customer_id
        LEFT JOIN products p
            ON o.product_id = p.product_id
        GROUP BY
            CAST(o.order_date AS DATE),
            c.region,
            p.product_category
        ORDER BY order_date, region, product_category
    """).fetchdf()

    # Gold 3: customer features — direct bridge to ML.
    features = con.execute("""
        WITH customer_orders AS (
            SELECT
                customer_id,
                COUNT(DISTINCT order_id) AS total_orders,
                SUM(quantity) AS total_units,
                SUM(net_amount) AS total_spend,
                AVG(net_amount) AS average_order_value,
                AVG(discount_pct) AS average_discount,
                AVG(customer_rating) AS average_rating,
                MIN(order_date) AS first_order_date,
                MAX(order_date) AS last_order_date
            FROM orders
            GROUP BY customer_id
        ),
        ranked_products AS (
            SELECT
                o.customer_id,
                p.product_category,
                SUM(o.quantity) AS category_units,
                ROW_NUMBER() OVER (
                    PARTITION BY o.customer_id
                    ORDER BY SUM(o.quantity) DESC, p.product_category
                ) AS category_rank
            FROM orders o
            JOIN products p
                ON o.product_id = p.product_id
            GROUP BY o.customer_id, p.product_category
        )
        SELECT
            c.customer_id,
            c.customer_name,
            c.segment,
            c.region,
            co.total_orders,
            co.total_units,
            co.total_spend,
            co.average_order_value,
            co.average_discount,
            co.average_rating,
            co.first_order_date,
            co.last_order_date,
            rp.product_category AS favorite_category
        FROM customers c
        LEFT JOIN customer_orders co
            ON c.customer_id = co.customer_id
        LEFT JOIN ranked_products rp
            ON c.customer_id = rp.customer_id
           AND rp.category_rank = 1
    """).fetchdf()

    enriched.to_parquet(GOLD / "enriched_orders.parquet",
                        compression="snappy", index=False)
    sales.to_parquet(GOLD / "sales_summary.parquet",
                     compression="snappy", index=False)
    features.to_parquet(GOLD / "customer_features.parquet",
                        compression="snappy", index=False)

    result = {
        "enriched_orders": len(enriched),
        "sales_summary": len(sales),
        "customer_features": len(features),
    }

    con.close()
    return result

def main():
    require_inputs()
    clean_output()

    bronze = write_bronze()
    silver = write_silver()
    gold = write_gold()

    report = {
        "phase": 4,
        "layers": {
            "bronze": bronze,
            "silver": silver,
            "gold": gold,
        },
        "status": "PASS",
    }

    report_path = REPORTS / "pipeline_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 65)
    print("PHASE 4 — BRONZE / SILVER / GOLD PIPELINE")
    print("=" * 65)

    print("\nBRONZE")
    for k, v in bronze.items():
        print(f"  {k:12}: {v:,}")

    print("\nSILVER")
    for k, v in silver.items():
        print(f"  {k:12}: {v:,}")

    print("\nGOLD")
    for k, v in gold.items():
        print(f"  {k:20}: {v:,}")

    print("\nOutputs:")
    print("  data/bronze/")
    print("  data/silver/")
    print("  data/gold/")
    print(f"\nReport: {report_path}")

if __name__ == "__main__":
    main()
