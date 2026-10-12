from pathlib import Path
import json
import pandas as pd
BASE = Path(__file__).resolve().parents[1]

def test_ml_ready_files_exist():
    for name in ['customer_ml_ready.parquet','customer_ml_ready.csv','feature_dictionary.json']:
        assert (BASE/'data'/'ml_ready'/name).exists()

def test_ml_ready_has_no_missing_values():
    p=BASE/'data'/'ml_ready'/'customer_ml_ready.parquet'
    if not p.exists(): return
    assert not pd.read_parquet(p).isna().any().any()

def test_ml_ready_identifier_is_unique():
    p=BASE/'data'/'ml_ready'/'customer_ml_ready.parquet'
    if not p.exists(): return
    assert pd.read_parquet(p)['customer_id'].is_unique

def test_ml_features_are_numeric():
    p=BASE/'data'/'ml_ready'/'customer_ml_ready.parquet'
    if not p.exists(): return
    df=pd.read_parquet(p).drop(columns=['customer_id'])
    assert all(pd.api.types.is_numeric_dtype(t) for t in df.dtypes)

def test_feature_dictionary_exists():
    p=BASE/'data'/'ml_ready'/'feature_dictionary.json'
    if not p.exists(): return
    assert len(json.loads(p.read_text(encoding='utf-8'))) > 0
