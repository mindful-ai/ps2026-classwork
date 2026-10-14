import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

from src.validate import validate_data


def train_test_model():
    df = pd.read_csv("data/customers.csv")
    validate_data(df)
    X = df.drop(columns=["churn"])
    y = df["churn"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    return model, X_test, y_test


def test_model_quality():
    model, X_test, y_test = train_test_model()
    predictions = model.predict(X_test)
    score = f1_score(y_test, predictions, zero_division=0)
    # Instructional threshold only; choose a business-justified threshold in production.
    assert score >= 0.50, f"F1 below threshold: {score:.3f}"


def test_model_output():
    model, X_test, _ = train_test_model()
    predictions = model.predict(X_test.head(10))
    assert len(predictions) == min(10, len(X_test))
    assert set(predictions).issubset({0, 1})


def test_recall_by_group_helper():
    # Small generic helper example to illustrate subgroup metric calculation.
    from src.subgroup_metrics import recall_by_group

    result = recall_by_group(
        y_true=[1, 1, 0, 1],
        predictions=[1, 0, 0, 1],
        groups=["A", "A", "B", "B"],
    )
    assert set(result["group"]) == {"A", "B"}
    assert set(result.columns) == {"group", "samples", "recall"}
