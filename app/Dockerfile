FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev

COPY main.py ./

EXPOSE 8000

ENV UV_NO_DEV=1

CMD [ "uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0","--port", "8000" ]
