from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger("pipeline")

DATA_DIR = Path(
    os.getenv("PIPELINE_DATA_DIR", str(Path(__file__).resolve().parent.parent / "data"))
)
SOURCE_FILE = DATA_DIR / "orders.json"

OUTPUT_DIR = Path(os.getenv("PIPELINE_OUTPUT_DIR", "/tmp/pipeline"))
OUTPUT_FILE = OUTPUT_DIR / "revenue_by_region.parquet"


def ingest() -> pd.DataFrame:
    """Read the mocked source dataset."""
    logger.info("ingest: reading %s", SOURCE_FILE)
    df = pd.read_json(SOURCE_FILE)
    logger.info("ingest: %d raw order rows", len(df))
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Total revenue and order count per region."""
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    out = (
        df.groupby("region", as_index=False)
        .agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)  # type: ignore[call-overload]
        .reset_index(drop=True)
    )
    out["revenue"] = out["revenue"].round(2)
    logger.info("transform: %d aggregated region rows", len(out))
    return out


def persist(df: pd.DataFrame) -> None:
    """Write the result to Parquet. Idempotent: the file is overwritten each run."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_FILE, index=False)
    logger.info("persist: wrote %d rows to %s", len(df), OUTPUT_FILE)


def run() -> dict:
    """Run the full pipeline; return a small summary."""
    result = transform(ingest())
    persist(result)
    return {"status": "ok", "rows": int(len(result)), "output": str(OUTPUT_FILE)}


def read_result(limit: int = 100) -> dict:
    if not OUTPUT_FILE.exists():
        return {"status": "empty", "rows": 0, "records": []}
    df = pd.read_parquet(OUTPUT_FILE).head(limit)
    json_str = df.to_json(orient="records") or "[]"
    records = json.loads(json_str)
    return {"status": "ok", "rows": int(len(df)), "records": records}
