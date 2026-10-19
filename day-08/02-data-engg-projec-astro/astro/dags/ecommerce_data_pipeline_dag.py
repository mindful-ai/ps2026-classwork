"""Airflow DAG for the existing six-phase e-commerce data engineering project.

Place this file in the project's ``dags/`` directory. It reuses the existing
Python scripts and tests; each phase is exposed as a Python function and run
by a PythonOperator. The DAG is externally/manual triggered (schedule=None).
"""

from datetime import datetime, timedelta, timezone
import logging
import os
from pathlib import Path
import subprocess
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

# Expected layout:
# project_root/
#   dags/ecommerce_data_pipeline_dag.py
#   src/...
#   data/...
PROJECT_ROOT = Path(__file__).resolve().parents[1] / "project"
LOGGER = logging.getLogger(__name__)


def run_script(*args: str) -> None:
    """Run an existing project script and fail the Airflow task on errors."""
    command = [sys.executable, *args]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    LOGGER.info("Working directory: %s", PROJECT_ROOT)
    LOGGER.info("Running command: %s", " ".join(command))
    subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        env=env,
        check=True,
    )


def phase_1_data_and_sql_foundations() -> None:
    """Apply source mappings and run the SQL foundations examples."""
    run_script("src/apply_mappings.py")
    run_script("src/run_sql.py")


def phase_2_data_quality_and_trust() -> None:
    """Repair/prepare data, run validation, and execute validation tests."""
    run_script("src/repair_phase2_data_quality_upgraded.py", "--apply")
    run_script("src/validate.py")
    run_script("-m", "pytest", "-q", "src/test_validation.py")


def phase_3_storage_and_formats() -> None:
    """Create and validate storage-format outputs."""
    run_script("src/phase3_storage.py")


def phase_4_medallion_pipeline() -> None:
    """Build the Bronze, Silver, and Gold datasets."""
    run_script("src/pipeline.py")


def phase_5_production_practices() -> None:
    """Run production checks and their tests."""
    run_script("src/production_pipeline.py")
    run_script("-m", "pytest", "-q", "src/test_phase5.py")


def phase_6_ml_ready_dataset() -> None:
    """Build, inspect, and test the ML-ready dataset."""
    run_script("src/build_ml_ready_upgraded.py")
    run_script("src/inspect_ml_ready.py")
    run_script("-m", "pytest", "-q", "src/test_phase6.py")


DEFAULT_ARGS = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="ecommerce_data_pipeline",
    description="Run the existing six-phase e-commerce data engineering pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    schedule=None,  # Trigger manually or through the authenticated Airflow API.
    catchup=False,
    max_active_runs=1,  # Prevent overlapping writes to local project files.
    dagrun_timeout=timedelta(hours=4),
    tags=["ecommerce", "data-engineering", "six-phases"],
    doc_md=__doc__,
) as dag:
    task_phase_1 = PythonOperator(
        task_id="phase_1_data_and_sql_foundations",
        python_callable=phase_1_data_and_sql_foundations,
        execution_timeout=timedelta(hours=1),
    )

    task_phase_2 = PythonOperator(
        task_id="phase_2_data_quality_and_trust",
        python_callable=phase_2_data_quality_and_trust,
        execution_timeout=timedelta(hours=1),
    )

    task_phase_3 = PythonOperator(
        task_id="phase_3_storage_and_formats",
        python_callable=phase_3_storage_and_formats,
        execution_timeout=timedelta(hours=1),
    )

    task_phase_4 = PythonOperator(
        task_id="phase_4_bronze_silver_gold",
        python_callable=phase_4_medallion_pipeline,
        execution_timeout=timedelta(hours=1),
    )

    task_phase_5 = PythonOperator(
        task_id="phase_5_production_checks",
        python_callable=phase_5_production_practices,
        execution_timeout=timedelta(hours=1),
    )

    task_phase_6 = PythonOperator(
        task_id="phase_6_ml_ready_dataset",
        python_callable=phase_6_ml_ready_dataset,
        execution_timeout=timedelta(hours=1),
    )

    (
        task_phase_1
        >> task_phase_2
        >> task_phase_3
        >> task_phase_4
        >> task_phase_5
        >> task_phase_6
    )
