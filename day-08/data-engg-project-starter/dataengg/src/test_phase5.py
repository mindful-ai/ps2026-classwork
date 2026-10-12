from pathlib import Path
import json, subprocess, sys
import pandas as pd
BASE=Path(__file__).resolve().parents[1]

def test_production_directories_exist():
    for r in ('data/production/staging','data/production/failed','reports/runs'): assert (BASE/r).exists()

def test_gold_order_ids_unique():
    p=BASE/'data/gold/enriched_orders.parquet'
    if p.exists(): assert not pd.read_parquet(p).order_id.duplicated().any()

def test_run_report_structure():
    rs=sorted((BASE/'reports/runs').glob('*.json'))
    if rs:
        x=json.loads(rs[-1].read_text()); assert {'run_id','status','started_at','completed_at'}<=x.keys()

def test_pipeline_is_repeatable():
    if not (BASE/'data/bronze/orders.parquet').exists(): return
    cmd=[sys.executable,str(BASE/'src/production_pipeline.py')]
    a=subprocess.run(cmd,cwd=BASE,capture_output=True,text=True); assert a.returncode==0,a.stdout+a.stderr
    n1=len(pd.read_parquet(BASE/'data/gold/enriched_orders.parquet'))
    b=subprocess.run(cmd,cwd=BASE,capture_output=True,text=True); assert b.returncode==0,b.stdout+b.stderr
    n2=len(pd.read_parquet(BASE/'data/gold/enriched_orders.parquet')); assert n1==n2
