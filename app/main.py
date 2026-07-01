import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from logging_config import configure_logging
from pipeline import read_result, run
from pipeline.pipeline import OUTPUT_DIR

configure_logging()
logger = logging.getLogger("app")

APP_VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(title="DataOps pipeline app", version=APP_VERSION)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    logger.info(
        "request",
        extra={
            "extra_fields": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    return response


@app.get("/")
def root():
    return {"service": "dataops-pipeline-app", "version": APP_VERSION}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        writable = os.access(OUTPUT_DIR, os.W_OK)
    except OSError:
        writable = False
    if not writable:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "output_dir": str(OUTPUT_DIR)},
        )
    return {"status": "ok", "output_dir": str(OUTPUT_DIR)}


@app.post("/pipeline/run")
def pipeline_run():
    """Trigger the data pipeline. The work happens here in the app, not in Airflow.

    Defined as a sync function so FastAPI runs it in a threadpool — the blocking
    pandas work won't stall the event loop.
    """
    logger.info(
        "pipeline.run: starting", extra={"extra_fields": {"event": "pipeline_start"}}
    )
    summary = run()
    logger.info(
        "pipeline.run: done",
        extra={"extra_fields": {"event": "pipeline_done", **summary}},
    )
    return summary


@app.get("/pipeline/result")
def pipeline_result():
    return read_result()
