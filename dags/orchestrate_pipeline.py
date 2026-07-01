from __future__ import annotations

from typing import Any

import pendulum
import requests
from airflow.sdk import Variable, dag, task


def _base_url() -> str:
    return Variable.get("APP_BASE_URL")


@dag(
    dag_id="orchestrate_pipeline",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["dataops", "pipeline"],
    default_args={"retries": 1, "retry_delay": pendulum.duration(seconds=10)},
)
def orchestrate_pipeline():
    @task
    def check_health() -> None:
        resp = requests.get(f"{_base_url()}/health", timeout=10)
        resp.raise_for_status()
        assert resp.json().get("status") == "ok", f"unexpected health: {resp.text}"

    @task
    def run_pipeline() -> dict:
        resp = requests.post(f"{_base_url()}/pipeline/run", timeout=60)
        resp.raise_for_status()
        return resp.json()

    @task
    def verify_result(run_summary: dict | Any) -> None:
        resp = requests.get(f"{_base_url()}/pipeline/result", timeout=30)
        resp.raise_for_status()
        result = resp.json()
        rows = result.get("rows", 0)
        if rows < 1:
            raise ValueError(f"pipeline produced no rows: {result}")
        print(f"verified {rows} rows persisted; run summary was {run_summary}")

    health = check_health()
    summary = run_pipeline()
    _ = health >> summary
    verify_result(summary)


orchestrate_pipeline()
