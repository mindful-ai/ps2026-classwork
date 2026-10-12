import pandas as pd

products = pd.read_csv("products.csv")
products.to_parquet("products.parquet", index=False)
print("Created products.parquet")
