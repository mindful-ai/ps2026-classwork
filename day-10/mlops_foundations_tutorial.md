# MLOps Foundations: A Practical Industry-Oriented Tutorial

This tutorial covers lifecycle reproducibility, experiment tracking, model registry, quality gates, and CI/CD for machine learning. The hands-on example uses Python, MLflow, scikit-learn, Git, pytest, and GitHub Actions.

## 1. Learning objectives

By the end, you should be able to:

- Track data, code, dependencies, experiments, models, and deployments.
- Use MLflow to record parameters, metrics, and artifacts.
- Version datasets and models and reproduce a selected experiment.
- Register models, manage versions, and implement promotion workflows.
- Build data-schema, model-performance, bias, and acceptance checks.
- Automate tests and quality gates through CI/CD.
- Produce traceable, versioned model artifacts for deployment.

## 2. The MLOps lifecycle

1. **Data and features:** dataset versions, schema, feature definitions.
2. **Code and environment:** Git commit, dependency lockfile, configuration.
3. **Experiments:** MLflow parameters, metrics, artifacts, run comparison.
4. **Quality gates:** data validation, model evaluation, bias checks, tests.
5. **Model registry:** versioning, approval, ownership, model card.
6. **CI/CD and deployment:** automated tests, immutable artifact, release, monitoring.

A model is not production-ready merely because its accuracy is high. Its origin, dependencies, data, evaluation evidence, approval status, and deployment version must also be traceable.

## 3. Tutorial project: Customer churn prediction

We will build a small binary classifier that predicts whether a customer will leave a service. The synthetic dataset is for learning the workflow only; it is not evidence about real customer churn.

| Component | Technology | Purpose |
|---|---|---|
| Source control | Git | Version training and validation code |
| Dataset | CSV + SHA-256 | Identify exact training data |
| Model | scikit-learn | Train a classifier |
| Experiment tracking | MLflow | Record runs and compare results |
| Quality gates | pytest | Validate data and model performance |
| Model registry | MLflow Model Registry | Manage registered versions |
| CI/CD | GitHub Actions | Test changes automatically |
| Serving extension | FastAPI | Expose inference through an API |

### 3.1 Project structure

```text
mlops-foundations/
├── data/
│   └── customers.csv             # generated locally
├── src/
│   ├── __init__.py
│   ├── make_data.py
│   ├── train.py
│   ├── validate.py
│   └── register_model.py
├── tests/
│   ├── test_data.py
│   └── test_model.py
├── artifacts/                    # local reports
├── .github/workflows/ci.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

### 3.2 Set up the environment

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For production, use a tested, pinned dependency set and a lockfile. The requirements in this tutorial are deliberately simple and should be pinned for a controlled production build.

## 4. Lifecycle and reproducibility

Reproducibility means being able to identify the conditions that produced a model and, where practical, reproduce its results.

| Item | What to record | Example |
|---|---|---|
| Source code | Git commit SHA | commit identifier |
| Dataset | Version, checksum, source | `customers.csv` + SHA-256 |
| Features | Names, order, transformations | `tenure`, `monthly_charges` |
| Environment | Python and package versions | locked dependencies |
| Experiment | Parameters and metrics | `C=1.0`, `f1=0.84` |
| Model | Serialized artifact and signature | registered model version |
| Deployment | Artifact version and configuration | staging release identifier |

The example logs the dataset checksum and Git commit. A checksum identifies file contents but does not preserve the dataset or document its lineage. For larger systems, use dataset versioning or a data platform that records source, transformations, schema, and lineage.

Generate the deterministic synthetic dataset:

```bash
python -m src.make_data
```

Calculate a dataset checksum:

```python
import hashlib

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()

print(sha256_file("data/customers.csv"))
```

If the CSV changes, its checksum will almost certainly change too.

## 5. Experiment management with MLflow

MLflow Tracking records:
- **Parameters:** hyperparameters and configuration.
- **Metrics:** accuracy, precision, recall, F1 score, latency, and more.
- **Artifacts:** model files, plots, reports, schemas, and other outputs.
- **Metadata:** Git commit, dataset hash, environment details, and run identifiers.

Start the local UI:

```bash
mlflow ui --host 127.0.0.1 --port 5000
```

Open <http://127.0.0.1:5000>. In this local tutorial, MLflow uses a local tracking configuration. Team deployments should configure shared tracking and artifact storage.

Train the model:

```bash
python -m src.train
```

Try different regularization settings on Windows PowerShell:

```powershell
$env:MODEL_C="0.1"
python -m src.train
$env:MODEL_C="1.0"
python -m src.train
$env:MODEL_C="10.0"
python -m src.train
```

On macOS/Linux:

```bash
MODEL_C=0.1 python -m src.train
MODEL_C=1.0 python -m src.train
MODEL_C=10.0 python -m src.train
```

In the MLflow UI, compare the runs using F1, precision, recall, and accuracy. Record the best run ID and dataset checksum. Repeat the selected configuration and compare the results.

Reproducible code and data do not guarantee identical results in every environment. Library versions, hardware, randomness, and nondeterministic operations can affect results.

## 6. Model registry and promotion

Experiment tracking answers: **How did this model perform?**

The model registry answers: **Which model version is approved for use, and what is its lifecycle status?**

Register a model from a completed run:

```bash
python -m src.register_model --run-id YOUR_RUN_ID
```

The script registers the logged model under `CustomerChurnModel`. Configure a suitable backend and artifact store for registry operations; requirements vary by MLflow version and deployment setup.

A production model lifecycle typically includes:

1. Train and evaluate a candidate.
2. Register the candidate and preserve its run metadata.
3. Run release quality gates.
4. Record reviewer approval and ownership.
5. Promote the exact validated artifact.
6. Keep the prior production version available for rollback.

Modern MLflow workflows can use model aliases such as `candidate` and `champion`. A newer version is not necessarily a better model, and registry metadata alone does not establish that a model is fair, safe, or approved.

### Model-card evidence

For every production model, maintain:
- Model name, version, and owner.
- Intended use and prohibited uses.
- Training dataset and data limitations.
- Feature definitions and target variable.
- Evaluation metrics and test methodology.
- Performance across relevant customer groups.
- Known risks and limitations.
- Approval date, reviewer, and deployment reference.
- Monitoring and rollback procedures.

## 7. Quality gates: validation before release

A quality gate is a rule that must pass before a model proceeds to the next lifecycle stage. For example, a release should stop if required columns are missing or F1 is below an agreed threshold.

Validate the dataset:

```bash
python -m src.validate
```

Run tests:

```bash
pytest -v
```

The included checks validate required columns, missing values, basic value ranges, target values, prediction output, and a simple F1 threshold.

The F1 threshold in this project is an instructional example. Industrial thresholds should be justified by business costs, a validated baseline, class imbalance, and the relative costs of false positives and false negatives.

### Bias and subgroup performance

Overall metrics can hide poor performance for a particular group. For example, a churn model may have acceptable overall recall but miss more churners in one region or customer segment.

The sample test suite includes a simple subgroup recall helper to illustrate how group-level evaluation can be added. In a real system:
- Define groups and acceptance criteria before evaluating the final candidate.
- Check sample sizes and uncertainty.
- Select fairness metrics appropriate to the application.
- Investigate meaningful differences rather than assuming one universal threshold defines fairness.
- Ensure audit use of group attributes complies with privacy requirements and applicable law.

The synthetic data in this tutorial is not evidence of real-world fairness.

### Example release policy

| Gate | Example acceptance rule | Failure action |
|---|---|---|
| Data schema | Required columns and types valid | Stop pipeline |
| Data integrity | No prohibited nulls or invalid target values | Stop pipeline |
| Model quality | F1 at least 0.75 | Reject candidate |
| Recall | At least 0.70 | Reject candidate |
| Bias assessment | No unexplained material subgroup disparity | Manual review |
| Unit tests | All required tests pass | Block merge/release |
| Approval | Authorized reviewer approves candidate | Do not promote |

These thresholds are illustrative, not recommended production values. Quality gates should be executable rules where possible, with human review for risks that cannot be reduced to a numeric threshold.

## 8. CI/CD for machine learning

- **Continuous integration (CI):** Run code checks, unit tests, data validation, and model tests when a pull request is opened or updated.
- **Continuous delivery (CD):** Package a validated candidate and make it available for controlled release.
- **Continuous deployment:** Automatically release a candidate when all required checks and policies permit it.

The GitHub Actions workflow in `.github/workflows/ci.yml` generates the synthetic dataset, validates it, and runs tests on pushes and pull requests.

After creating a Git repository and pushing this project to GitHub, inspect the Actions tab to see the workflow result.

For real applications, validate a governed, versioned test dataset rather than relying only on generated synthetic data. Avoid exposing sensitive production data in CI logs or artifacts.

### Immutable artifacts

An immutable artifact is a specific, identifiable model package that is not overwritten after validation. A release should record:
- Model artifact URI and checksum.
- MLflow run ID and registered model version.
- Git commit and dependency lockfile.
- Dataset version or checksum.
- Quality-gate results.
- Approval record and deployment configuration.

Build once, validate the candidate, and promote the same artifact through staging and production. Do not retrain independently in each environment and assume the models are identical.

## 9. Hands-on completion checklist

- [ ] Create the project structure and install dependencies.
- [ ] Generate the dataset with `python -m src.make_data`.
- [ ] Validate data with `python -m src.validate`.
- [ ] Start MLflow and run `python -m src.train`.
- [ ] Try multiple values of `MODEL_C` and compare metrics.
- [ ] Run `pytest -v`.
- [ ] Register a selected run with `python -m src.register_model --run-id YOUR_RUN_ID`.
- [ ] Push the repository and inspect GitHub Actions.

## 10. Industry practices to adopt

| Practice | Why it matters |
|---|---|
| Version datasets and features | Reproduce training inputs |
| Track code and environment | Reconstruct training conditions |
| Track every experiment | Explain model selection |
| Store evaluation evidence | Make approval auditable |
| Enforce automated quality gates | Prevent invalid releases |
| Register model versions | Maintain lifecycle governance |
| Build immutable artifacts | Avoid environment-to-environment drift |
| Use approval policies | Control production promotion |
| Monitor production performance | Detect data drift and degradation |
| Maintain rollback capability | Recover from a bad release |

## 11. Important distinctions

- **Experiment tracking is not data versioning.** A checksum alone does not preserve a dataset or its lineage.
- **A model registry is not an approval process by itself.** Define who can approve and promote candidates and what evidence is required.
- **Passing tests is not proof of fairness.** Fairness evaluation requires suitable groups, metrics, sample sizes, and domain-specific criteria.
- **CI is not the entire MLOps pipeline.** Production delivery also requires artifact management, release controls, deployment, monitoring, and rollback.
- **Reproducibility is broader than a random seed.** It includes data, source code, dependencies, configuration, and execution conditions.

## 12. Suggested next extension: FastAPI and containers

Extend the project with a FastAPI inference service and Docker or Podman packaging:

1. Load the approved model version from MLflow.
2. Expose a `/predict` endpoint.
3. Add request-schema validation and prediction tests.
4. Build a container image tagged with a release identifier.
5. Run API integration tests against that image.
6. Deploy to staging, validate health and latency, and promote the same image to production.

This connects lifecycle reproducibility, experiment tracking, registry governance, quality gates, and CI/CD into a practical MLOps release workflow.
