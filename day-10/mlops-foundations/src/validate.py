import pandas as pd

FEATURES = ["tenure", "monthly_charges", "support_calls"]
TARGET = "churn"


def validate_data(df: pd.DataFrame) -> bool:
    required = FEATURES + [TARGET]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    if df.empty:
        raise ValueError("Dataset is empty")

    if df[required].isnull().any().any():
        raise ValueError("Missing values found")

    if not df["tenure"].between(1, 72).all():
        raise ValueError("Invalid tenure values")

    if not df["monthly_charges"].between(0, 200).all():
        raise ValueError("Invalid monthly charges")

    if not df["support_calls"].between(0, 20).all():
        raise ValueError("Invalid support call count")

    if not df[TARGET].isin([0, 1]).all():
        raise ValueError("Target must contain only 0 and 1")

    if df[TARGET].nunique() != 2:
        raise ValueError("Both target classes must be present")

    return True


if __name__ == "__main__":
    data = pd.read_csv("data/customers.csv")
    validate_data(data)
    print("Data validation passed")
