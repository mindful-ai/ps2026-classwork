# Astronomer project add-on

The original project remains unchanged in `dataengg/`. The `project/` directory is a runtime copy of the existing project inside this Astro build context so Airflow task containers can access the existing scripts and data.

## Run locally

From this `astro` directory, run `astro dev start`, then trigger `ecommerce_data_pipeline` from the Airflow UI. The DAG uses `schedule=None`, so it runs only when manually or externally triggered.
