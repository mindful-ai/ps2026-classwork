# Machine Learning Models Reference

A practical reference of commonly used Machine Learning models, their Python modules/libraries, probable use cases, and why they are useful.

---

# 1. Regression

Regression is used when the target/output is a **continuous numerical value**.

| Machine Learning Model | Module / Library | Probable Use Case & Why |
|---|---|---|
| Linear Regression | `sklearn.linear_model.LinearRegression` | **House price prediction** — simple, interpretable relationship between features and price. |
| Ridge Regression | `sklearn.linear_model.Ridge` | **Price prediction with many correlated features** — regularization reduces overfitting. |
| Lasso Regression | `sklearn.linear_model.Lasso` | **Feature selection + prediction** — can drive unimportant feature coefficients to zero. |
| Elastic Net | `sklearn.linear_model.ElasticNet` | **High-dimensional datasets** — combines Ridge and Lasso regularization. |
| Polynomial Regression | `sklearn.preprocessing.PolynomialFeatures` + `LinearRegression` | **Non-linear relationships** — models curves while retaining a linear-regression framework. |
| Decision Tree Regressor | `sklearn.tree.DecisionTreeRegressor` | **Customer spending prediction** — captures non-linear relationships and feature interactions. |
| Random Forest Regressor | `sklearn.ensemble.RandomForestRegressor` | **Sales/revenue prediction** — robust, handles non-linear data and feature effects. |
| Gradient Boosting Regressor | `sklearn.ensemble.GradientBoostingRegressor` | **Demand forecasting** — often highly accurate on structured/tabular data. |
| Extra Trees Regressor | `sklearn.ensemble.ExtraTreesRegressor` | **Large tabular datasets** — randomized trees can provide good accuracy with relatively little tuning. |
| HistGradientBoosting Regressor | `sklearn.ensemble.HistGradientBoostingRegressor` | **Large datasets** — faster gradient boosting implementation for many rows. |
| XGBoost | `xgboost.XGBRegressor` | **Kaggle/business prediction problems** — powerful gradient-boosted trees with extensive tuning options. |
| LightGBM | `lightgbm.LGBMRegressor` | **Very large tabular datasets** — fast and memory efficient. |
| CatBoost | `catboost.CatBoostRegressor` | **Datasets with categorical variables** — handles categorical features particularly well. |
| Support Vector Regression | `sklearn.svm.SVR` | **Small/medium datasets with complex relationships** — kernel functions model non-linearity. |
| K-Nearest Neighbors Regressor | `sklearn.neighbors.KNeighborsRegressor` | **Similarity-based prediction** — predicts from nearby observations. |
| Neural Network Regressor | `sklearn.neural_network.MLPRegressor` / `tensorflow` / `torch` | **Complex non-linear prediction** — useful when traditional algorithms are insufficient. |
| Gaussian Process Regression | `sklearn.gaussian_process.GaussianProcessRegressor` | **Small datasets requiring uncertainty estimates** — provides prediction and uncertainty. |

### Typical Regression Targets

- Price
- Salary
- Temperature
- Demand
- Revenue
- House value
- Delivery time
- Energy consumption

---

# 2. Classification

Classification is used when the target is a **category or class**.

| Machine Learning Model | Module / Library | Probable Use Case & Why |
|---|---|---|
| Logistic Regression | `sklearn.linear_model.LogisticRegression` | **Customer churn: Yes/No** — simple, fast and highly interpretable baseline. |
| K-Nearest Neighbors | `sklearn.neighbors.KNeighborsClassifier` | **Customer/category classification** — classifies based on similar observations. |
| Decision Tree Classifier | `sklearn.tree.DecisionTreeClassifier` | **Loan approval** — easy-to-understand decision rules. |
| Random Forest Classifier | `sklearn.ensemble.RandomForestClassifier` | **Fraud detection / risk classification** — robust and handles non-linear relationships. |
| Extra Trees Classifier | `sklearn.ensemble.ExtraTreesClassifier` | **Large tabular classification** — randomized trees provide strong performance. |
| Gradient Boosting Classifier | `sklearn.ensemble.GradientBoostingClassifier` | **Risk prediction** — powerful for structured/tabular data. |
| HistGradientBoosting Classifier | `sklearn.ensemble.HistGradientBoostingClassifier` | **Large tabular classification** — efficient gradient boosting. |
| XGBoost | `xgboost.XGBClassifier` | **Fraud/churn/credit-risk prediction** — excellent performance on structured data. |
| LightGBM | `lightgbm.LGBMClassifier` | **Large-scale classification** — fast and efficient. |
| CatBoost | `catboost.CatBoostClassifier` | **Classification with categorical features** — excellent handling of categorical variables. |
| Support Vector Machine | `sklearn.svm.SVC` | **Text/image/small dataset classification** — effective in high-dimensional feature spaces. |
| Naive Bayes | `sklearn.naive_bayes` | **Spam/email/text classification** — fast and particularly effective for word-count features. |
| Linear SVM | `sklearn.svm.LinearSVC` | **Document/text classification** — efficient for high-dimensional sparse data. |
| Neural Network / MLP | `sklearn.neural_network.MLPClassifier` | **Complex classification** — learns non-linear decision boundaries. |
| CNN | `tensorflow.keras` / `torch.nn` | **Image classification** — learns spatial features directly from images. |
| RNN / LSTM / GRU | `tensorflow.keras` / `torch.nn` | **Sequence classification** — useful for time-series or sequential data. |
| Transformer | `transformers` / `torch` / `tensorflow` | **Text classification, NLP, multimodal tasks** — captures long-range contextual relationships. |

### Typical Classification Targets

- Spam / Not Spam
- Fraud / Not Fraud
- Disease / No Disease
- Rice type
- Customer segment
- Sentiment
- Defective / Non-defective

---

# 3. Clustering

Clustering is used when there is **no predefined target/class** and we want the algorithm to discover groups in the data.

| Machine Learning Model | Module / Library | Probable Use Case & Why |
|---|---|---|
| K-Means | `sklearn.cluster.KMeans` | **Customer segmentation** — simple and fast when clusters are roughly spherical. |
| Mini-Batch K-Means | `sklearn.cluster.MiniBatchKMeans` | **Very large customer datasets** — faster and more memory efficient than standard K-Means. |
| DBSCAN | `sklearn.cluster.DBSCAN` | **Geographical/location data** — finds dense groups and identifies outliers automatically. |
| HDBSCAN | `hdbscan` | **Complex customer/geographical clusters** — handles varying cluster densities better than DBSCAN. |
| Agglomerative Clustering | `sklearn.cluster.AgglomerativeClustering` | **Hierarchical customer segmentation** — produces a hierarchy of clusters. |
| Mean Shift | `sklearn.cluster.MeanShift` | **Image/feature segmentation** — discovers the number of clusters automatically. |
| Gaussian Mixture Model | `sklearn.mixture.GaussianMixture` | **Customer segmentation with overlapping groups** — gives probability of belonging to each cluster. |
| Spectral Clustering | `sklearn.cluster.SpectralClustering` | **Non-spherical clusters** — useful when traditional K-Means fails. |
| Birch | `sklearn.cluster.Birch` | **Large datasets** — designed for efficient incremental clustering. |
| Self-Organizing Map | `MiniSom` / custom neural network | **Visualization and pattern discovery** — maps high-dimensional data onto a 2D grid. |
| Autoencoder-based Clustering | `tensorflow` / `torch` | **Complex high-dimensional data** — learns useful representations before clustering. |
| Deep Embedded Clustering | `torch` / `tensorflow` implementations | **Images/high-dimensional data** — combines representation learning with clustering. |

### Typical Clustering Applications

- Customer segmentation
- Product grouping
- Anomaly discovery
- Document grouping
- Image grouping
- Geographical segmentation

---

# Quick Mental Model

| Type | Question Being Answered | Example |
|---|---|---|
| **Regression** | **"How much?"** | What will this house cost? |
| **Classification** | **"Which class?"** | Is this transaction fraudulent? |
| **Clustering** | **"Which group?"** | What natural customer groups exist? |

---

# Recommended Learning Order

For a general-purpose Machine Learning course, a useful progression is:

## Regression

**Linear Regression**  
→ **Ridge / Lasso**  
→ **Decision Tree**  
→ **Random Forest**  
→ **Gradient Boosting**  
→ **XGBoost / LightGBM / CatBoost**

## Classification

**Logistic Regression**  
→ **KNN**  
→ **Decision Tree**  
→ **Random Forest**  
→ **SVM**  
→ **Naive Bayes**  
→ **Gradient Boosting**  
→ **XGBoost / LightGBM / CatBoost**  
→ **Neural Networks**

## Clustering

**K-Means**  
→ **Hierarchical Clustering**  
→ **DBSCAN**  
→ **Gaussian Mixture Models**  
→ **HDBSCAN**  
→ **Deep Clustering**

This progression moves from **simple and interpretable models → ensemble models → advanced/deep-learning approaches**.
