\
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "phase1"
MAP = ROOT / "data" / "mappings"
OUT.mkdir(parents=True, exist_ok=True)
MAP.mkdir(parents=True, exist_ok=True)

CUSTOMER_NAMES = [
    "Anil Kumar", "Priya Sharma", "Ravi Menon", "Sneha Reddy",
    "Arjun Nair", "Meera Iyer", "Vikram Singh", "Kavya Rao",
    "Rahul Verma", "Pooja Nair", "Suresh Babu", "Divya Krishnan",
    "Amit Patel", "Neha Gupta", "Kiran Joshi", "Lakshmi Rao",
    "Manoj Kumar", "Shreya Das", "Nitin Sharma", "Deepa Menon",
    "Rohit Reddy", "Swati Iyer", "Ajay Nair", "Ananya Rao",
    "Sanjay Kumar", "Asha Singh", "Vivek Patel", "Nandini Gupta",
    "Prakash Joshi", "Ritu Verma",
]

PRODUCTS = [
    ("43\" LED TV", "Television", "Samsung"),
    ("55\" 4K Smart TV", "Television", "LG"),
    ("Galaxy A55 5G", "Mobile", "Samsung"),
    ("iPhone 15", "Mobile", "Apple"),
    ("Pavilion 15 Laptop", "Laptop", "HP"),
    ("IdeaPad Slim 5", "Laptop", "Lenovo"),
    ("260L Frost-Free Refrigerator", "Refrigerator", "LG"),
    ("7 kg Front Load Washing Machine", "Washing Machine", "IFB"),
    ("Bluetooth Portable Speaker", "Audio", "Sony"),
    ("Noise Cancelling Headphones", "Audio", "Sony"),
    ("Air Fryer 4.5L", "Kitchen", "Philips"),
    ("Mixer Grinder 750W", "Kitchen", "Preethi"),
    ("Microwave Oven 25L", "Kitchen", "IFB"),
    ("Smart Watch Series 2", "Wearables", "Noise"),
    ("Wireless Keyboard and Mouse", "Computer Accessories", "Logitech"),
    ("1TB Portable SSD", "Storage", "Samsung"),
    ("Wi-Fi 6 Router", "Networking", "TP-Link"),
    ("20,000mAh Power Bank", "Mobile Accessories", "Mi"),
    ("USB-C Fast Charger 65W", "Mobile Accessories", "Anker"),
    ("Robot Vacuum Cleaner", "Home Appliances", "Eureka Forbes"),
    ("Water Purifier RO", "Home Appliances", "Kent"),
    ("2 Door Wardrobe", "Furniture", "Wakefit"),
    ("Office Chair", "Furniture", "Green Soul"),
    ("Non-Stick Cookware Set", "Kitchen", "Prestige"),
    ("Cotton Double Bedsheet", "Home Furnishing", "Spaces"),
    ("Running Shoes", "Footwear", "Puma"),
    ("Casual Sneakers", "Footwear", "Skechers"),
    ("Travel Backpack 30L", "Bags", "American Tourister"),
    ("Electric Kettle 1.5L", "Kitchen", "Prestige"),
]

def require(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Copy the previously generated CSV into data/raw/."
        )

def choose_name(i):
    if i < len(CUSTOMER_NAMES):
        return CUSTOMER_NAMES[i]
    return f"Customer {i+1:04d}"

def main():
    for name in ["orders.csv", "customers.csv", "products.csv"]:
        require(RAW / name)

    customers = pd.read_csv(RAW / "customers.csv")
    products = pd.read_csv(RAW / "products.csv")
    orders = pd.read_csv(RAW / "orders.csv")

    if "customer_id" not in customers.columns:
        raise ValueError("customers.csv must contain customer_id")
    if "product_id" not in products.columns:
        raise ValueError("products.csv must contain product_id")
    if not {"customer_id", "product_id"}.issubset(orders.columns):
        raise ValueError("orders.csv must contain customer_id and product_id")

    # Customer mapping: preserve IDs; replace/add realistic names.
    existing_customer_name = "customer_name" in customers.columns
    customer_map = pd.DataFrame({"customer_id": customers["customer_id"].astype(str)})
    customer_map["customer_name_mapped"] = [
        choose_name(i) for i in range(len(customer_map))
    ]
    customer_map.to_csv(MAP / "customer_mapping.csv", index=False)

    customers["customer_id"] = customers["customer_id"].astype(str)
    customers["customer_name"] = customer_map["customer_name_mapped"]
    customers.to_csv(OUT / "customers_mapped.csv", index=False)

    # Product mapping: preserve IDs; replace/add realistic product attributes.
    product_map_rows = []
    for i, pid in enumerate(products["product_id"].astype(str)):
        item = PRODUCTS[i % len(PRODUCTS)]
        product_map_rows.append({
            "product_id": pid,
            "product_name_mapped": item[0],
            "product_category_mapped": item[1],
            "brand_mapped": item[2],
        })
    product_map = pd.DataFrame(product_map_rows)
    product_map.to_csv(MAP / "product_mapping.csv", index=False)

    products["product_id"] = products["product_id"].astype(str)
    products["product_name"] = product_map["product_name_mapped"]
    if "product_category" in products.columns:
        products["product_category"] = product_map["product_category_mapped"]
    else:
        products["product_category"] = product_map["product_category_mapped"]
    if "brand" not in products.columns:
        products["brand"] = product_map["brand_mapped"]
    else:
        products["brand"] = product_map["brand_mapped"]
    products.to_csv(OUT / "products_mapped.csv", index=False)

    orders["customer_id"] = orders["customer_id"].astype(str)
    orders["product_id"] = orders["product_id"].astype(str)
    orders.to_csv(OUT / "orders_mapped.csv", index=False)

    print("Phase 1 mapping complete.")
    print(f"Customers: {len(customers):,}")
    print(f"Products : {len(products):,}")
    print(f"Orders   : {len(orders):,}")
    print("\nOutput:")
    print("  data/phase1/customers_mapped.csv")
    print("  data/phase1/products_mapped.csv")
    print("  data/phase1/orders_mapped.csv")

if __name__ == "__main__":
    main()
