# AG News Text Classification — Class Project

**Goal:** Build and explain a multi-class news topic classifier using rich text feature engineering and two model families (Logistic Regression and Random Forest).  
**Dataset:** AG News (4 classes: World, Sports, Business, Sci/Tech).

---

## 1) Dataset & Downloads

Use the CSV version (no login needed):

- **Train (120,000 rows):**  
  https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/train.csv
- **Test (7,600 rows):**  
  https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/test.csv
- **Class names:**  
  1 = World, 2 = Sports, 3 = Business, 4 = Sci/Tech

> Each CSV has 3 columns: `label,title,description` (no header row).

---

## 2) Learning Outcomes

- Practice **text-focused feature engineering** (cleaning, simple numeric signals, TF‑IDF + SVD).
- Compare a **linear** classifier vs a **tree-based** classifier on text features.
- Perform **hyperparameter tuning** with cross-validation.
- Apply **explainability**: permutation importance + a lightweight SHAP demo.
- Deliver a clean **inference** workflow for new text inputs.

---

## 3) What You’ll Build

A full pipeline that:
1. Loads and cleans the dataset.
2. Engineers features from raw text.
3. Builds a `ColumnTransformer` to combine numeric + text pipelines.
4. Trains **Logistic Regression** and **Random Forest** classifiers.
5. Tunes hyperparameters with `GridSearchCV`.
6. Evaluates with **accuracy, precision/recall/F1, confusion matrix**.
7. Explains model behavior (global and local).
8. Makes a **sample prediction** on arbitrary news text.

---

## 4) Environment Setup

Recommended packages:
```
pip install pandas scikit-learn textblob shap matplotlib
python -m textblob.download_corpora
```
> If you’re in Colab, run the above in a cell. SHAP plots need a graphical backend.

---

## 5) Step-by-Step Activities (Student Tasks)

### A. Data Loading & EDA
1. Download `train.csv` and `test.csv` and load with `pd.read_csv(..., header=None, names=['label','title','description'])`.
2. Combine `title` + `description` into a single `text` field.
3. Check class balance and a few example rows.

### B. Cleaning & Feature Engineering
4. Implement a `clean_text` function: lowercase, strip HTML, keep letters, collapse spaces.
5. Create numeric features: `char_len`, `word_count`, `excl_count` (`!` count).
6. (Optional) Add `polarity` from `TextBlob`.
7. Split into train/test using the provided CSVs (do not resplit).

### C. Preprocessing Pipelines
8. Define numeric pipeline: `SimpleImputer(median)` → `StandardScaler`.
9. Define text pipeline: `TfidfVectorizer(max_features=10000, stop_words='english')` → `TruncatedSVD(n_components=100)`.
10. Combine with `ColumnTransformer`.

### D. Modeling
11. Build two pipelines (each ends with a classifier):
    - Logistic Regression (`LogisticRegression(max_iter=1000)`)
    - Random Forest (`RandomForestClassifier(n_estimators=200)`)
12. Train both; compute metrics on the official test set.

### E. Hyperparameter Tuning
13. Use `GridSearchCV` to tune:
    - LR: `C` ∈ {0.1, 1, 10}
    - RF: `n_estimators` ∈ {100, 300}, `max_depth` ∈ {None, 20}
14. Report best params and cross-val accuracy.

### F. Explainability
15. **Permutation Importance** on the best model; plot top 20 features.  
    > For feature names: numeric feature names + `svd_0 ... svd_99`.
16. **SHAP (lightweight):** compute on a **random sample of 200 test rows** and render a summary plot.

### G. Sample Prediction
17. Create a small helper that takes a raw `title` + `description` and prints predicted class + probability.

### H. Deliverables
18. A short write‑up (1–2 pages) addressing:
    - Which model performed better and why?
    - What features matter most?
    - Example explanations on 2–3 test samples.
19. Your final notebook/script.

---

## 6) Stretch Goals (Optional)
- Remove SVD and train LR on raw TF‑IDF; inspect top n‑grams per class (via coefficients).
- Try a linear SVM (`LinearSVC`) and compare macro F1.
- Add bigrams in TF‑IDF and compare.
- Perform **error analysis**: where do models disagree?

---

## 7) Grading Rubric (Guide)
- Data & EDA (10%)
- Feature Engineering + Pipelines (25%)
- Modeling & Tuning (25%)
- Explainability (20%)
- Inference & Write‑up (20%)
