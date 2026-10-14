import pandas as pd
import pytest

from src.make_data import create_dataset
from src.validate import validate_data


def test_generated_data_passes_validation(tmp_path):
    output = tmp_path / "customers.csv"
    create_dataset(output_path=str(output), n=200, seed=42)
    df = pd.read_csv(output)
    assert validate_data(df) is True


def test_missing_column_fails():
    df = pd.DataFrame({
        "tenure": [1, 2],
        "monthly_charges": [20.0, 30.0],
        "churn": [0, 1],
    })
    with pytest.raises(ValueError, match="Missing columns"):
        validate_data(df)


def test_missing_values_fail():
    df = pd.DataFrame({
        "tenure": [1, 2],
        "monthly_charges": [20.0, None],
        "support_calls": [0, 1],
        "churn": [0, 1],
    })
    with pytest.raises(ValueError, match="Missing values"):
        validate_data(df)
