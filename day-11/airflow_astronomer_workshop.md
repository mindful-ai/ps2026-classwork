# 🚀 Workshop: Apache Airflow with Astronomer (Step-by-Step Guide)

This guide walks you through setting up **Astronomer’s Astro CLI**, running **Airflow locally**, and building two simple DAGs. It also covers optional deployment to Astronomer Cloud.

---

## 0. Prerequisites
- **Container runtime**: Astro CLI defaults to **Podman** (you can switch to Docker).  
- **OS**: Works on macOS, Windows, Linux.  
- **Ports**: 8080 (Airflow UI) and 5432 (Postgres) must be free.  

---

## 1. Install Astro CLI

### macOS (Homebrew)
```bash
brew install astro
```

### Windows (winget)
```powershell
winget install -e --id Astronomer.Astro
```

### Linux (install script)
```bash
curl -sSL https://install.astronomer.io | bash
```

### (Optional) Switch to Docker instead of Podman
```bash
astro config set container.binary docker -g
```

---

## 2. Create an Astro Project
```bash
mkdir airflow-workshop && cd airflow-workshop
astro dev init --from-template learning-airflow
```

This generates:
- `dags/` → where DAGs live  
- `Dockerfile` → image config  
- `requirements.txt` → Python deps  
- `airflow_settings.yaml` → variables, connections  

---

## 3. Run Airflow Locally
```bash
astro dev start
```

- Open **http://localhost:8080**  
- Login: **admin / admin**  

Useful commands:
```bash
astro dev ps        # running containers
astro dev stop      # stop without deleting volumes
astro dev restart   # rebuild + restart
```

---

## 4. Example DAGs

### A) TaskFlow API DAG
Create `dags/taskflow_mini_etl.py`:

```python
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
```

➡️ Demo in UI: Turn DAG **on**, trigger it, and check **Graph View**.

---

### B) Classic Operators DAG
Create `dags/hello_ops.py`:

```python
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

def greet(name: str):
    print(f"Hello, {name}! 👋")

with DAG(
    dag_id="hello_ops",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["workshop", "operators"]
) as dag:
    print_date = BashOperator(
        task_id="print_date",
        bash_command="date"
    )

    say_hello = PythonOperator(
        task_id="say_hello",
        python_callable=greet,
        op_kwargs={"name": "Airflow"},
    )

    print_date >> say_hello
```

➡️ Demo in UI: Trigger manually, check **Logs + Gantt/Graph view**.

---

## 5. Manage Connections and Variables (Optional)
Use `airflow_settings.yaml` for declarative configs:

```bash
astro dev object import
```

---

## 6. Deploy to Astronomer Cloud (Optional)

1. Login:
```bash
astro login
```

2. Deploy project:
```bash
astro deploy
```

---

## 7. Astro CLI Cheat-Sheet
| Action | Command |
|--------|---------|
| Create project | `astro dev init --from-template learning-airflow` |
| Start local env | `astro dev start` |
| List containers | `astro dev ps` |
| Stop env | `astro dev stop` |
| Restart env | `astro dev restart` |
| Bash into scheduler | `astro dev bash -s` |
| Switch runtime | `astro config set container.binary docker -g` |
| Deploy to Astronomer | `astro login` → `astro deploy` |

---

## 8. Troubleshooting
- **Ports in use (8080/5432):** Stop other services or re-map ports.  
- **New deps not found:** Add to `requirements.txt` → run `astro dev restart`.  
- **Preserve state when stopping:** Use `astro dev stop` instead of killing containers.  

---

✅ You now have Astronomer + Airflow running with example DAGs!


```bash
podman machine inspect --format '{{.ConnectionInfo.PodmanPipe.Path}}'
$env:DOCKER_HOST = "npipe:////./pipe/podman-machine-default"
```