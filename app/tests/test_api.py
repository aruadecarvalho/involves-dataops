from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready_ok():
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_run_then_result():
    run = client.post("/pipeline/run")
    assert run.status_code == 200
    assert run.json()["rows"] >= 1

    result = client.get("/pipeline/result")
    assert result.status_code == 200
    body = result.json()
    assert body["rows"] >= 1
    assert {"region", "orders", "revenue"} <= set(body["records"][0].keys())
