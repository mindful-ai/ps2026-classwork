# MLOps Foundations — Customer Churn Tutorial

This project demonstrates lifecycle reproducibility, MLflow experiment tracking, model registration, data validation, model-quality tests, and CI with GitHub Actions.

## Requirements
- Python 3.10+ (Python 3.12 is used in CI)
- Git
- Internet access for initial package installation

## Quick start

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Generate the synthetic dataset:
```bash
python -m src.make_data
```

Validate data and run tests:
```bash
python -m src.validate
pytest -v
```

Start MLflow UI in one terminal:
```bash
mlflow ui --host 127.0.0.1 --port 5000
```

Train in another terminal:
```bash
python -m src.train
```

Open http://127.0.0.1:5000 to inspect runs and artifacts. Try different hyperparameters:

Windows PowerShell:
```powershell
$env:MODEL_C="0.1"; python -m src.train
$env:MODEL_C="1.0"; python -m src.train
$env:MODEL_C="10.0"; python -m src.train
```

macOS/Linux:
```bash
MODEL_C=0.1 python -m src.train
MODEL_C=1.0 python -m src.train
MODEL_C=10.0 python -m src.train
```

Register a run:
```bash
python -m src.register_model --run-id YOUR_RUN_ID
```

## Important notes
- `data/customers.csv` is generated locally and is not included in the ZIP.
- The dataset is synthetic and only for learning.
- Quality thresholds are educational examples and must be selected for the actual business problem.
- MLflow registry support depends on the configured backend store and MLflow version. If registration is not supported by your local setup, configure a registry-capable backend/tracking server.
- For production, pin and lock dependencies, preserve dataset versions, use secure artifact storage, protect secrets, and add deployment monitoring and rollback.
