export APP_IMAGE_NAME ?= involves-fastapi:latest
export APP_CONTAINER_NAME ?= involves-fastapi-service

.PHONY: up down restart

up:
	docker compose up -d
	docker build -t $(APP_IMAGE_NAME) app
	docker run --rm -d -p 8000:8000 --name $(APP_CONTAINER_NAME) $(APP_IMAGE_NAME)

down:
	docker compose down
	-docker stop $(APP_CONTAINER_NAME)

restart: down up

app-build:
	docker build -t $(IMAGE) app/

pipeline:
	cd app && uv run python -m pipeline

lint:
	uvx ruff check app dags

fmt:
	uvx ruff format app dags
