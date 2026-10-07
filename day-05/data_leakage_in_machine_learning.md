# Data Leakage in Machine Learning

**Data leakage** in Machine Learning means:

> **Information that would not be available when making a real-world prediction accidentally gets into the training process.**

The result is usually a model that looks **much better during testing than it will perform in reality**.

---

## Simple Example

Suppose you want to predict whether a customer will **churn**.

Your data contains:

| Feature | Meaning |
|---|---|
| Age | Customer age |
| MonthlySpend | Current spending |
| ContractType | Current contract |
| **CancellationDate** | Date customer actually cancelled |
| Churn | Target |

If you give `CancellationDate` to the model:

```text
CancellationDate → Churn
```

the model can easily learn:

> "If cancellation date exists → customer churned."

You might get:

```text
Accuracy = 99%
```

but this is meaningless. When predicting a **future customer**, you won't know their cancellation date.

That's **data leakage**.

---

## Another Very Common Example: Preprocessing

Suppose you have:

```python
X_train, X_test, y_train, y_test
```

and you do:

```python
scaler.fit(X)       # ❌ Leakage
X_scaled = scaler.transform(X)
```

The scaler has now seen information from **both training and test data**.

Correct:

```python
scaler.fit(X_train)       # ✅
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

This is one reason using a **scikit-learn `Pipeline` with `preprocessor`** is a good practice:

```python
pipe_lr = Pipeline([
    ('pre', preprocessor),
    ('clf', LogisticRegression())
])
```

The preprocessing is fitted only on the training portion during model fitting.

---

## The Key Question

Whenever building an ML model, ask:

> **"Would this information actually be available at the exact moment I need to make the prediction?"**

If the answer is **No**, you probably have leakage.

---

## Common Types of Leakage

| Leakage Type | Example |
|---|---|
| **Target leakage** | A feature directly or indirectly contains information about the target |
| **Train-test leakage** | Test data influences training/preprocessing |
| **Temporal leakage** | Future information is used to predict the past |
| **Feature engineering leakage** | A feature is calculated using information unavailable at prediction time |
| **Duplicate leakage** | Almost identical records appear in both train and test sets |

---

## Rule of Thumb

```text
Training data
     ↓
Only information available at prediction time
     ↓
Model
     ↓
Prediction
```

If information from **the future, the test set, or the target** sneaks backward into training, you have leakage.
