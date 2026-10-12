from pathlib import Path
import pandas as pd
BASE = Path(__file__).resolve().parents[1]
df = pd.read_parquet(BASE / 'data' / 'ml_ready' / 'customer_ml_ready.parquet')
print('\nML-READY DATASET')
print('=' * 60)
print(f'Rows    : {len(df)}')
print(f'Columns : {len(df.columns)}')
print('\nColumns:')
for c in df.columns: print(f'  - {c}')
print('\nSample:')
print(df.head(10).to_string(index=False))
print('\nMissing values:')
print(df.isna().sum())
