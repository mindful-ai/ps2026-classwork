from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys, traceback
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
BRONZE, SILVER, GOLD = BASE/'data/bronze', BASE/'data/silver', BASE/'data/gold'
STAGING, FAILED, RUNS = BASE/'data/production/staging', BASE/'data/production/failed', BASE/'reports/runs'
for p in (STAGING, FAILED, RUNS): p.mkdir(parents=True, exist_ok=True)

def now(): return datetime.now(timezone.utc).isoformat()
def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def fingerprint_inputs():
    out={}
    for layer in (BRONZE, SILVER):
        if layer.exists():
            for p in sorted(layer.glob('*.parquet')):
                out[str(p.relative_to(BASE))]={'rows':len(pd.read_parquet(p)), 'sha256':sha256(p)}
    return out

def quality_gate():
    required=[SILVER/'orders.parquet', SILVER/'customers.parquet', SILVER/'products.parquet', BRONZE/'orders.parquet']
    for p in required:
        if not p.exists(): raise RuntimeError(f'Missing required input: {p.relative_to(BASE)}')
    o=pd.read_parquet(SILVER/'orders.parquet'); c=pd.read_parquet(SILVER/'customers.parquet'); p=pd.read_parquet(SILVER/'products.parquet')
    bo=pd.read_parquet(BRONZE/'orders.parquet')
    checks={
        'orders_not_empty':len(o)>0, 'customers_not_empty':len(c)>0, 'products_not_empty':len(p)>0,
        'order_ids_unique':not o.order_id.duplicated().any(),
        'customer_ids_unique':not c.customer_id.duplicated().any(),
        'product_ids_unique':not p.product_id.duplicated().any(),
        'required_order_values_valid':o.customer_id.notna().all() and o.product_id.notna().all() and o.quantity.notna().all() and (o.quantity>0).all() and (o.unit_price>=0).all() and o.discount_pct.between(0,100).all(),
        'customer_fk_valid':o.customer_id.isin(c.customer_id).all(),
        'product_fk_valid':o.product_id.isin(p.product_id).all(),
        'bronze_silver_row_count_reconciles':len(bo)==len(o),
    }
    return {'passed':all(checks.values()),'checks':checks,'row_counts':{'bronze_orders':len(bo),'silver_orders':len(o),'customers':len(c),'products':len(p)}}

def build_gold():
    o=pd.read_parquet(SILVER/'orders.parquet'); c=pd.read_parquet(SILVER/'customers.parquet'); p=pd.read_parquet(SILVER/'products.parquet')
    e=o.merge(c,on='customer_id',how='left',validate='many_to_one').merge(p,on='product_id',how='left',validate='many_to_one')
    if e.customer_name.isna().any() or e.product_name.isna().any(): raise RuntimeError('Unresolved foreign-key references during Gold build')
    s=(e.groupby(['order_date','region','product_category'],as_index=False).agg(order_count=('order_id','nunique'),units=('quantity','sum'),gross_sales=('gross_amount','sum'),discount_amount=('discount_amount','sum'),net_sales=('net_amount','sum')))
    cf=(e.groupby(['customer_id','customer_name','segment','region'],as_index=False).agg(total_orders=('order_id','nunique'),total_units=('quantity','sum'),total_spend=('net_amount','sum'),average_order_value=('net_amount','mean'),average_discount=('discount_pct','mean'),average_rating=('customer_rating','mean'),first_order_date=('order_date','min'),last_order_date=('order_date','max')))
    cq=e.groupby(['customer_id','product_category'],as_index=False).agg(category_units=('quantity','sum'))
    cq['rank']=cq.groupby('customer_id')['category_units'].rank(method='first',ascending=False)
    fav=cq[cq['rank']==1][['customer_id','product_category']].rename(columns={'product_category':'favorite_category'})
    cf=cf.merge(fav,on='customer_id',how='left')
    return {'enriched_orders':e,'sales_summary':s,'customer_features':cf}

def promote(tables, run_id):
    stage=STAGING/run_id; stage.mkdir(parents=True,exist_ok=False)
    try:
        for name,df in tables.items(): df.to_parquet(stage/f'{name}.parquet',index=False)
        for name,df in tables.items():
            p=stage/f'{name}.parquet'
            if not p.exists() or len(pd.read_parquet(p))!=len(df): raise RuntimeError(f'Staging verification failed: {name}')
        GOLD.mkdir(parents=True,exist_ok=True)
        for p in GOLD.glob('*.parquet'): p.unlink()
        for p in stage.glob('*.parquet'): shutil.copy2(p,GOLD/p.name)
    except Exception:
        failed=FAILED/run_id
        if failed.exists(): shutil.rmtree(failed)
        shutil.move(str(stage),str(failed)); raise
    finally:
        if stage.exists(): shutil.rmtree(stage)

def main():
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report={'run_id':run_id,'started_at':now(),'status':'STARTED','pipeline':'ecommerce_phase5_production'}
    try:
        report['input_fingerprint']=fingerprint_inputs()
        report['quality_gate']=quality_gate()
        if not report['quality_gate']['passed']: raise RuntimeError('Production quality gate failed')
        tables=build_gold(); report['gold_row_counts']={k:len(v) for k,v in tables.items()}
        promote(tables,run_id); report['status']='SUCCESS'
    except Exception as exc:
        report['status']='FAILED'; report['error']=str(exc); report['traceback']=traceback.format_exc()
    report['completed_at']=now(); (RUNS/f'{run_id}.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))
    return 0 if report['status']=='SUCCESS' else 1

if __name__=='__main__': sys.exit(main())
