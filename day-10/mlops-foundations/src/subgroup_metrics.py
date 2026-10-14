import pandas as pd
from sklearn.metrics import recall_score


def recall_by_group(y_true, predictions, groups):
    evaluation = pd.DataFrame({
        "actual": list(y_true),
        "predicted": list(predictions),
        "group": list(groups),
    })

    results = []
    for group, part in evaluation.groupby("group"):
        recall = recall_score(
            part["actual"], part["predicted"], zero_division=0
        )
        results.append({
            "group": group,
            "samples": len(part),
            "recall": recall,
        })

    return pd.DataFrame(results)
