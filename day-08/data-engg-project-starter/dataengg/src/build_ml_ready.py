from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
GOLD = BASE / 'data' / 'gold'
OUT = BASE / 'data' / 'ml_ready'
REPORTS = BASE / 'reports' / 'ml'
OUT.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

def main():
    src = GOLD / 'customer_features.parquet'
    if not src.exists():
        raise FileNotFoundError(f'Missing Gold dataset: {src}. Run earlier phases first.')
    df = pd.read_parquet(src)
    required = ['customer_id','segment','region','total_orders','total_units','total_spend',
                'average_order_value','average_discount','average_rating',
                'first_order_date','last_order_date','favorite_category']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f'Missing Gold columns: {missing}')

    x = df.copy()
    x['first_order_date'] = pd.to_datetime(x['first_order_date'])
    x['last_order_date'] = pd.to_datetime(x['last_order_date'])
    ref = x['last_order_date'].max()
    x['customer_tenure_days'] = (x['last_order_date'] - x['first_order_date']).dt.days.clip(lower=0)
    x['recency_days'] = (ref - x['last_order_date']).dt.days.clip(lower=0)

    model = x[['customer_id','segment','region','favorite_category','total_orders','total_units',
               'total_spend','average_order_value','average_discount','average_rating',
               'customer_tenure_days','recency_days']].copy()
    encoded = pd.get_dummies(model, columns=['segment','region','favorite_category'], dtype=int)
    ids = encoded['customer_id']
    features = encoded.drop(columns=['customer_id']).fillna(0)
    ml = features.copy()
    ml.insert(0, 'customer_id', ids.values)

    checks = {
        'not_empty': len(ml) > 0,
        'customer_id_unique': ml['customer_id'].is_unique,
        'no_missing_values': not ml.isna().any().any(),
        'numeric_features_only': all(pd.api.types.is_numeric_dtype(t) for t in ml.drop(columns=['customer_id']).dtypes),
        'spend_non_negative': (ml['total_spend'] >= 0).all(),
        'orders_positive': (ml['total_orders'] > 0).all(),
        'units_positive': (ml['total_units'] > 0).all(),
    }
    if not all(checks.values()):
        raise RuntimeError('ML-ready quality gate failed: ' + json.dumps(checks))

    ml.to_parquet(OUT / 'customer_ml_ready.parquet', index=False)
    ml.to_csv(OUT / 'customer_ml_ready.csv', index=False)
    dictionary = []
    for c in ml.columns:
        role = 'identifier' if c == 'customer_id' else ('categorical_encoded' if c.startswith(('segment_','region_','favorite_category_')) else 'numeric_feature')
        dictionary.append({'feature': c, 'role': role, 'dtype': str(ml[c].dtype), 'missing_values': int(ml[c].isna().sum())})
    (OUT / 'feature_dictionary.json').write_text(json.dumps(dictionary, indent=2), encoding='utf-8')
    report = {'source': 'data/gold/customer_features.parquet', 'rows': len(ml), 'columns': len(ml.columns), 'feature_count': len(ml.columns)-1, 'validation': {'passed': True, 'checks': checks}}
    (REPORTS / 'ml_ready_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
