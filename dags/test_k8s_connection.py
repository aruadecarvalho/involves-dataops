from datetime import datetime

import requests
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import Variable


def check_app_connection():
    url = Variable.get("APP_BASE_URL")
    response = requests.get(url)
    response.raise_for_status()

    print(f"Success, app returned: {response.json()}")


with DAG(
    dag_id="verify_k8s_connection",
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:
    PythonOperator(task_id="ping_app", python_callable=check_app_connection)
