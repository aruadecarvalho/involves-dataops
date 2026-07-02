FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv

COPY main.py logging_config.py ./
COPY pipeline ./pipeline
COPY data ./data

ENV PATH="/app/.venv/bin:$PATH"
ENV PIPELINE_OUTPUT_DIR=/data/output

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
