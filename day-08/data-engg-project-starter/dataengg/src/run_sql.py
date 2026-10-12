\
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "phase1_queries.sql"

def main():
    con = duckdb.connect()
    script = SQL.read_text(encoding="utf-8")
    statements = [s.strip() for s in script.split(";") if s.strip()]

    for i, statement in enumerate(statements, 1):
        try:
            result = con.execute(statement)
            if result.description:
                print(f"\n--- Query {i} ---")
                print(result.fetch_df().to_string(index=False))
        except Exception as exc:
            print(f"\nQuery {i} FAILED:\n{exc}")

    con.close()

if __name__ == "__main__":
    main()
