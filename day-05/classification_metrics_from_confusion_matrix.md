# Classification Metrics: From Confusion Matrix to ROC-AUC

## 1. Start with the Confusion Matrix

For a binary classification problem, suppose the model predicts:

- **Positive** — e.g., customer will churn
- **Negative** — e.g., customer will not churn

| | **Actual Positive** | **Actual Negative** |
|---|---:|---:|
| **Predicted Positive** | **TP** — True Positive | **FP** — False Positive |
| **Predicted Negative** | **FN** — False Negative | **TN** — True Negative |

Where:

- **TP**: Predicted positive, actually positive
- **TN**: Predicted negative, actually negative
- **FP**: Predicted positive, actually negative
- **FN**: Predicted negative, actually positive

Everything else follows from these four numbers.

---

## 2. Accuracy

### Question

> **"Out of everything I predicted, how many predictions were correct?"**

Correct predictions are:

```text
TP + TN
```

Total predictions are:

```text
TP + TN + FP + FN
```

Therefore:

$$
\boxed{
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}
}
$$

### Example

Suppose:

```text
TP = 80
TN = 90
FP = 10
FN = 20
```

Then:

$$
Accuracy = \frac{80+90}{80+90+10+20}
$$

$$
= \frac{170}{200} = 0.85
$$

So:

**Accuracy = 85%**

### Importance

Accuracy is useful when the classes are **reasonably balanced** and the costs of FP and FN are similar.

### Problem with Accuracy

Consider:

```text
990 customers → No Churn
10 customers  → Churn
```

A model that predicts **No Churn for everybody** gets:

$$
Accuracy = \frac{990}{1000}=99\%
$$

Sounds excellent—but the model identifies **zero churners**.

Therefore, accuracy alone can be misleading for **imbalanced datasets**.

---

## 3. Precision

Now we ask a different question:

> **"When the model says Positive, how often is it correct?"**

Look only at **Predicted Positive**:

```text
TP + FP
```

Among these, the correctly predicted positives are:

```text
TP
```

Therefore:

$$
\boxed{
Precision = \frac{TP}{TP+FP}
}
$$

### Example

```text
TP = 80
FP = 10
```

Therefore:

$$
Precision = \frac{80}{80+10}
$$

$$
= 0.889
$$

So:

**Precision = 88.9%**

### Importance

Precision is important when **false positives are expensive**.

For example, suppose a fraud detection system says:

> "This transaction is fraudulent."

If it incorrectly flags legitimate customers, that creates problems.

You therefore want:

**High Precision → When the model says Positive, it should usually be right.**

---

## 4. Recall

Now we ask:

> **"Of all the actual Positive cases, how many did the model find?"**

All actual positives are:

```text
TP + FN
```

The model correctly identified:

```text
TP
```

Therefore:

$$
\boxed{
Recall = \frac{TP}{TP+FN}
}
$$

Recall is also called:

- **Sensitivity**
- **True Positive Rate (TPR)**

### Example

```text
TP = 80
FN = 20
```

Therefore:

$$
Recall = \frac{80}{80+20}
$$

$$
= 0.80
$$

So:

**Recall = 80%**

### Importance

Recall is important when **missing a positive case is expensive or dangerous**.

Examples:

- Disease detection
- Fraud detection
- Defect detection
- Security threat detection
- Churn detection

For example, in medical screening:

> Missing a patient who actually has a disease can be much worse than sending a healthy patient for further testing.

Therefore, we generally want **high recall**.

---

## 5. Precision vs Recall

This is one of the most important concepts in classification.

Consider a churn model.

### Precision asks:

> **"Of the customers I predicted will churn, how many actually churn?"**

$$
Precision = \frac{TP}{TP+FP}
$$

### Recall asks:

> **"Of all customers who actually churned, how many did I identify?"**

$$
Recall = \frac{TP}{TP+FN}
$$

So:

```text
Precision → Trust my positive predictions

Recall    → Don't miss actual positives
```

---

## 6. F1-Score

Now we have two competing objectives:

- Precision
- Recall

We want a single metric that balances both.

A simple arithmetic average would be:

$$
\frac{Precision+Recall}{2}
$$

But F1 uses the **harmonic mean** instead:

$$
\boxed{
F1 = 2 \times
\frac{Precision \times Recall}
{Precision + Recall}
}
$$

After substituting the definitions of Precision and Recall and simplifying:

$$
\boxed{
F1 =
\frac{2TP}
{2TP+FP+FN}
}
$$

### Example

Suppose:

```text
Precision = 0.889
Recall    = 0.800
```

Then:

$$
F1 =
2\times
\frac{0.889\times0.800}
{0.889+0.800}
$$

$$
F1 \approx 0.842
$$

So:

**F1 = 84.2%**

### Importance

F1 is particularly useful when:

- Classes are imbalanced
- Both FP and FN matter
- You want a balance between precision and recall

A useful intuition:

```text
High Precision + Low Recall
        ↓
      F1 ↓

Low Precision + High Recall
        ↓
      F1 ↓

High Precision + High Recall
        ↓
      F1 ↑
```

---

## 7. From Confusion Matrix to ROC

Now we move to **ROC-AUC**.

There is an important difference:

**Accuracy, Precision, Recall and F1 are calculated from a particular classification threshold.**

For example:

```text
Probability > 0.5 → Positive
Probability ≤ 0.5 → Negative
```

But why must we use 0.5?

We don't necessarily have to.

Suppose the model produces:

```text
Customer A → 0.91
Customer B → 0.73
Customer C → 0.61
Customer D → 0.42
Customer E → 0.18
```

We could choose:

```text
Threshold = 0.5
```

or:

```text
Threshold = 0.7
```

Changing the threshold changes TP, FP, FN and TN.

ROC evaluates the model **across many thresholds**.

---

## 8. True Positive Rate

We already derived Recall:

$$
Recall = \frac{TP}{TP+FN}
$$

In ROC terminology:

$$
\boxed{
TPR = \frac{TP}{TP+FN}
}
$$

So:

$$
\boxed{TPR = Recall}
$$

---

## 9. False Positive Rate

Now consider the actual negative cases.

They consist of:

```text
TN + FP
```

Of these, the model incorrectly predicted Positive for:

```text
FP
```

Therefore:

$$
\boxed{
FPR = \frac{FP}{FP+TN}
}
$$

This is:

> **The proportion of actual negatives incorrectly classified as positive.**

---

## 10. ROC Curve

We now have two quantities:

$$
TPR = \frac{TP}{TP+FN}
$$

and

$$
FPR = \frac{FP}{FP+TN}
$$

The **ROC curve** plots:

$$
\boxed{TPR \text{ vs } FPR}
$$

at different classification thresholds.

Conceptually:

```text
TPR
1.0 |                 ●
    |             ●
    |          ●
    |       ●
    |    ●
    | ●
0.0 +------------------------ FPR
    0.0                    1.0
```

A good model tries to achieve:

```text
High TPR
+
Low FPR
```

In other words:

> **Find as many real positives as possible while incorrectly flagging as few negatives as possible.**

---

## 11. ROC-AUC

**AUC = Area Under the ROC Curve.**

It summarizes the ROC curve into a single number.

$$
\boxed{
ROC\text{-}AUC =
\text{Area under the ROC curve}
}
$$

The value ranges approximately from:

```text
0.5 → Random classifier
1.0 → Perfect classifier
```

A rough interpretation:

| ROC-AUC | Interpretation |
|---:|---|
| 0.50 | Random |
| 0.50–0.60 | Very weak |
| 0.60–0.70 | Poor |
| 0.70–0.80 | Reasonable |
| 0.80–0.90 | Good |
| 0.90–1.00 | Excellent |

These ranges are **rules of thumb**, not universal standards.

---

## 12. The Deeper Meaning of AUC

A very useful interpretation is:

> **ROC-AUC measures how well the model ranks positive examples above negative examples.**

For example:

```text
Actual Positive     Model probability
-------------------------------------
Customer A             0.91
Customer B             0.82
Customer C             0.71

Actual Negative
-------------------------------------
Customer D             0.31
Customer E             0.18
Customer F             0.07
```

The model is doing a good job putting positives above negatives.

Therefore:

```text
Positive probabilities
        ↓
  generally higher
        ↓
Negative probabilities
```

→ high ROC-AUC.

---

## 13. Putting Everything Together

Starting from the same four values:

```text
                    ACTUAL
                 P          N
              +-----------+-----------+
Predicted P   |    TP     |    FP     |
              +-----------+-----------+
Predicted N   |    FN     |    TN     |
              +-----------+-----------+
```

we derive:

### Accuracy

$$
\boxed{
Accuracy=\frac{TP+TN}{TP+TN+FP+FN}
}
$$

**Question:** How many predictions are correct overall?

---

### Precision

$$
\boxed{
Precision=\frac{TP}{TP+FP}
}
$$

**Question:** When I predict Positive, can I trust it?

---

### Recall

$$
\boxed{
Recall=\frac{TP}{TP+FN}
}
$$

**Question:** How many actual Positives did I find?

---

### F1

$$
\boxed{
F1=\frac{2TP}{2TP+FP+FN}
}
$$

**Question:** How well do I balance Precision and Recall?

---

### ROC

$$
\boxed{
TPR=\frac{TP}{TP+FN}
}
$$

$$
\boxed{
FPR=\frac{FP}{FP+TN}
}
$$

Plot:

$$
\boxed{TPR\;vs\;FPR}
$$

**Question:** How does the model behave as I change the classification threshold?

---

### ROC-AUC

$$
\boxed{
AUC = \text{Area under ROC curve}
}
$$

**Question:** How well does the model separate/rank positive cases above negative cases across thresholds?

---

# The Most Useful Mental Model

For your ML teaching, I would summarize them like this:

```text
                 CONFUSION MATRIX
              ┌─────────────────────┐
              │ TP  FP  FN  TN      │
              └─────────┬───────────┘
                        │
        ┌───────────────┼────────────────┐
        ↓               ↓                ↓
    Accuracy       Precision/Recall    ROC
        │               │                │
  "Overall,       "How good are     "What happens
   how often       my positive       when I change
   am I right?"    predictions?"     the threshold?"
                        │                │
                        ↓                ↓
                       F1             ROC-AUC
                        │                │
                  "Balance of       "Overall
                   precision        ranking/
                   & recall"        separation"
```

**One important teaching point:** **F1 and ROC-AUC answer different questions.** F1 evaluates performance at a chosen classification threshold, while ROC-AUC evaluates the model's discrimination across thresholds.
