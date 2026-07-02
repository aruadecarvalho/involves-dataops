# Involves DataOps

O Airflow (Docker Compose) orquestra via HTTP um app FastAPI rodando em Kubernetes (Kind). O app executa o pipeline de dados: lê pedidos de um JSON, agrega receita por região com pandas e grava o resultado em Parquet.

```
Airflow (Docker Compose, LocalExecutor)
  └─ DAG orchestrate_pipeline: check_health -> run_pipeline -> verify_result  (HTTP)
        └─ FastAPI no Kind: orders.json -> pandas -> Parquet (emptyDir)
```

## Pré-requisitos

Docker, [Kind](https://kind.sigs.k8s.io/), kubectl e Make. O uv só é necessário para rodar testes e o pipeline fora do contêiner.

## Como rodar

```bash
cp .env.example .env
make demo-up        # sobe o Airflow, cria o cluster Kind, builda e deploya o app
make port-forward   # em outro terminal, expõe o app em localhost:8000
```

1. Acesse o Airflow em <http://localhost:8080> (login `airflow`, senha `airflow`)
2. Despause e dispare a DAG `orchestrate_pipeline`
3. Confira o resultado: `curl http://localhost:8000/pipeline/result`

Para derrubar tudo: `make demo-down`

## Endpoints do app

| Endpoint | Descrição |
|---|---|
| `GET /health` | Liveness, o processo está vivo |
| `GET /ready` | Readiness, verifica se o diretório de saída é gravável |
| `POST /pipeline/run` | Executa o pipeline (ingestão, transformação, Parquet) |
| `GET /pipeline/result` | Lê o Parquet e retorna o agregado por região |

## Testes e lint

```bash
make test   # pytest do app (unidade + API) e das DAGs (integridade do DagBag)
make lint   # ruff check + format --check
```

## Estrutura

```
dags/                  # DAG que orquestra o app via HTTP, sem lógica de negócio
app/                   # FastAPI + pipeline (pandas) + testes
k8s/                   # Deployment, Service e ConfigMap
docker-compose.yml     # Airflow 3.2 com LocalExecutor + Postgres
.github/workflows/     # CI: lint, testes, kubeconform, build/push e e2e no Kind
```

## Troubleshooting

- Airflow não alcança o app (`Connection refused` no `check_health`): confirme que o `make port-forward` está rodando. Ele usa `--address 0.0.0.0` para que o contêiner do Airflow alcance o host via `host.docker.internal`.
- Cluster Kind sumiu (`current-context is not set`): `make k8s-up` recria e redeploya.
- `ImagePullBackOff`: o GC do containerd removeu a imagem do node. `make k8s-deploy` rebuilda e recarrega.
