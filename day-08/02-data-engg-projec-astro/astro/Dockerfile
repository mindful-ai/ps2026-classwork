FROM quay.io/astronomer/astro-runtime:12.8.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Include the existing project code and data in the task image.
COPY project /usr/local/airflow/project
