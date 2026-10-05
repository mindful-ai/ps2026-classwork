# SHAP in Machine Learning

## What is SHAP?

**SHAP (SHapley Additive exPlanations)** is a popular method to explain
predictions of machine learning models.\
It is based on **Shapley values** from cooperative game theory, which
determine how to fairly distribute the "payout" among players who worked
together to achieve a result.

In machine learning: - The **payout** is the model prediction. - The
**players** are the features of the dataset. - SHAP values tell us how
much each feature contributed to the prediction.

------------------------------------------------------------------------

## Why SHAP?

1.  **Interpretability**: Helps explain *why* a model made a certain
    prediction.\
2.  **Fairness**: Based on Shapley values, which provide a
    mathematically fair way to allocate contribution.\
3.  **Model-agnostic**: Works with many types of models (tree-based,
    deep learning, linear, etc.).

------------------------------------------------------------------------

## Example: Predicting Heart Disease

Imagine a model that predicts whether a patient has heart disease.\
Features: `Age`, `Cholesterol`, `Blood Pressure`, `Max Heart Rate`.

Suppose the model predicts: **High risk of heart disease**.\
Using SHAP, we can see contributions like:

-   **Age = 65** → +0.20 (increases risk)
-   **Cholesterol = 300** → +0.35 (increases risk)
-   **Blood Pressure = 120** → -0.05 (decreases risk)
-   **Max Heart Rate = 180** → -0.10 (decreases risk)

The **base value** (average model output) is adjusted by these
contributions to reach the final prediction.

------------------------------------------------------------------------

## Visualizations in SHAP

-   **Force plot**: Shows how features push the prediction higher or
    lower.
-   **Summary plot**: Shows the most important features across the
    dataset.
-   **Dependence plot**: Shows how a feature interacts with predictions.

------------------------------------------------------------------------

## Simple Code Example

``` python
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer

# Load dataset
X, y = load_breast_cancer(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = xgb.XGBClassifier().fit(X_train, y_train)

# Explain model predictions using SHAP
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Visualization (requires matplotlib)
shap.summary_plot(shap_values, X_test, feature_names=X.columns)
```

------------------------------------------------------------------------

## Key Takeaways

-   SHAP explains model predictions by fairly distributing contributions
    across features.
-   It helps make ML models **transparent, trustworthy, and
    explainable**.
-   Widely used in **healthcare, finance, and any domain** where
    decisions need justification.
