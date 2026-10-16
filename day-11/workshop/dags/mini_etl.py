from datetime import datetime
from airflow.decorators import dag, task

@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["workshop", "taskflow"]
)
def taskflow_mini_etl():
    @task
    def extract():
        return [2, 5, 7]

    @task
    def transform(numbers: list[int]) -> int:
        return sum(numbers)

    @task
    def load(total: int):
        print(f"[LOAD] Total = {total}")

    load(transform(extract()))

dag = taskflow_mini_etl()