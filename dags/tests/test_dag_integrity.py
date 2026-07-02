from pathlib import Path

from airflow.models import DagBag

DAGS_DIR = Path(__file__).resolve().parents[1]


def test_dags_import_without_errors():
    bag = DagBag(dag_folder=str(DAGS_DIR), include_examples=False)
    assert not bag.import_errors, bag.import_errors


def test_orchestrate_pipeline_dag_present():
    bag = DagBag(dag_folder=str(DAGS_DIR), include_examples=False)
    assert "orchestrate_pipeline" in bag.dags
