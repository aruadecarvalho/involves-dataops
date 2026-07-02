APP_IMAGE ?= fastapi-app:dev
KIND_CLUSTER ?= dataops
RUFF_VERSION         ?= ruff@0.15.20

.PHONY: demo-up demo-down af-up af-down restart-af app-build \
		kind-up k8s-deploy k8s-up port-forward k8s-down \
		app-pipeline lint fmt

demo-up: af-up k8s-up

demo-down: af-down k8s-down

af-up:
	docker compose up -d

af-down:
	docker compose down

restart-af: af-down af-up

app-build:
	docker build -t $(APP_IMAGE) app/

kind-up:
	kind get clusters | grep -q $(KIND_CLUSTER) || kind create cluster --name $(KIND_CLUSTER)

k8s-deploy: app-build
	kind load docker-image $(APP_IMAGE) --name $(KIND_CLUSTER)
	kubectl apply -f k8s/
	kubectl rollout restart deploy/fastapi-app
	kubectl rollout status deploy/fastapi-app --timeout=120s

k8s-up: kind-up k8s-deploy

port-forward:
	kubectl port-forward svc/fastapi-app 8000:80

k8s-down:
	kind delete cluster --name $(KIND_CLUSTER)

app-pipeline:
	cd app && uv run python -m pipeline

lint:
	uvx $(RUFF_VERSION) check app dags
	uvx $(RUFF_VERSION) format --check app dags

fmt:
	uvx $(RUFF_VERSION) format app dags
	uvx $(RUFF_VERSION) check --fix app dags

test: test-app test-dags

test-app:
	cd app && uv run --group dev pytest

test-dags:
	cd dags && uv run --group dev pytest
