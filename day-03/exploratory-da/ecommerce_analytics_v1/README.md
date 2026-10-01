# E-Commerce Analytics Dataset v1.0

Purpose-built for the Pandas/Matplotlib/Seaborn masterclass. The data intentionally contains realistic quality issues.

Files:
- orders.csv — 15,120 rows after intentional duplicates/issues
- customers.csv — 2,000 customers
- products.csv — 150 products
- convert_to_parquet.py — creates products.parquet with pandas + pyarrow
- INSTRUCTOR_DATA_QUALITY_GUIDE.md — instructor-only guide

To create Parquet after installing the engine:
```bash
pip install pyarrow
python convert_to_parquet.py
```
