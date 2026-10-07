# Understanding t-SNE (t-Distributed Stochastic Neighbor Embedding)

## What is t-SNE?

t-SNE (t-distributed Stochastic Neighbor Embedding) is a **non-linear
dimensionality reduction technique**. It is mainly used for
**visualizing high-dimensional data** in 2D or 3D while preserving the
structure of the data.

Unlike PCA (which focuses on global variance), t-SNE emphasizes **local
structure** by making sure that points that are close in
high-dimensional space remain close in the lower-dimensional space.

------------------------------------------------------------------------

## How Does t-SNE Work?

1.  **High-dimensional similarities**
    -   t-SNE computes probabilities that pairs of points are related
        (neighbors) in the high-dimensional space.\
    -   It uses a Gaussian distribution to measure similarities.
2.  **Low-dimensional similarities**
    -   It then defines a similar probability distribution in the
        low-dimensional (2D or 3D) space.\
    -   A Student's t-distribution (with heavy tails) is used to avoid
        the "crowding problem."
3.  **Minimizing the difference**
    -   The algorithm minimizes the **Kullback-Leibler (KL) divergence**
        between the high-dimensional and low-dimensional probability
        distributions.\
    -   This ensures that local neighborhoods are preserved.

------------------------------------------------------------------------

## Example in Practice

Suppose we have the **MNIST dataset** (handwritten digits). Each image
has 784 dimensions (28x28 pixels).

-   PCA can reduce it to \~50 dimensions.\
-   Then, applying **t-SNE** reduces it to 2D for visualization.\
-   The result shows clusters where each digit (0-9) forms its own
    group.

``` python
from sklearn.datasets import load_digits
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Load data
digits = load_digits()
X, y = digits.data, digits.target

# Apply t-SNE
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_embedded = tsne.fit_transform(X)

# Plot results
plt.figure(figsize=(10, 7))
plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=y, cmap='tab10', s=15)
plt.colorbar()
plt.title("t-SNE Visualization of Digits Dataset")
plt.show()
```

------------------------------------------------------------------------

## Key Parameters in t-SNE

-   **n_components**: Target dimension (2D or 3D).\
-   **perplexity**: Balances local vs. global structure. Typically
    between 5 and 50.\
-   **learning_rate**: Step size during optimization.\
-   **n_iter**: Number of iterations (default 1000, higher gives more
    stable results).

------------------------------------------------------------------------

## When to Use t-SNE?

-   Best for **visualization**, not for downstream ML tasks.\
-   Works well when you want to **see clusters** in high-dimensional
    datasets.\
-   Often used in **NLP (word embeddings)**, **bioinformatics (gene
    data)**, and **computer vision (image embeddings)**.

------------------------------------------------------------------------

## Limitations of t-SNE

-   **Computationally expensive** on large datasets.\
-   Results can vary across runs (non-deterministic).\
-   Does not preserve global structure well.\
-   Should not be used directly for prediction.

------------------------------------------------------------------------

## Summary

-   t-SNE is a powerful tool for **visualizing high-dimensional data in
    2D/3D**.\
-   It preserves **local neighborhood structures** but sacrifices global
    relationships.\
-   It is widely used for **exploratory data analysis**, especially in
    clustering contexts.
