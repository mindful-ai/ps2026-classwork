
import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate import check_schema, check_not_null, check_unique

def test_schema_passes():
    df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})
    result = check_schema(df, ["id", "name"])
    assert result["pass"]

def test_schema_detects_missing_column():
    df = pd.DataFrame({"id": [1, 2]})
    result = check_schema(df, ["id", "name"])
    assert not result["pass"]
    assert result["missing_columns"] == ["name"]

def test_null_rule():
    df = pd.DataFrame({"id": [1, None]})
    result = check_not_null(df, ["id"])
    assert not result["pass"]
    assert result["null_counts"]["id"] == 1

def test_unique_rule():
    df = pd.DataFrame({"id": [1, 1, 2]})
    result = check_unique(df, ["id"])
    assert not result["pass"]
    assert result["duplicate_value_rows"]["id"] == 2
