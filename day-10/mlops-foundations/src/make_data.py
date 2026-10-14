from pathlib import Path

import numpy as np
import pandas as pd


def create_dataset(output_path="data/customers.csv", n=1000, seed=42):
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 73, n)
    monthly_charges = rng.uniform(20, 120, n)
    support_calls = rng.integers(0, 10, n)

    logits = (
        1.5
        - 0.045 * tenure
        + 0.025 * (monthly_charges - 60)
        + 0.30 * support_calls
    )
    probability = 1 / (1 + np.exp(-logits))
    churn = rng.binomial(1, probability)

    df = pd.DataFrame({
        "tenure": tenure,
        "monthly_charges": monthly_charges.round(2),
        "support_calls": support_calls,
        "churn": churn,
    })

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Wrote {len(df)} rows to {path}")


if __name__ == "__main__":
    create_dataset()
