# Decisões técnicas

O que escolhi, o que abri mão e por quê.

## DAG fina, pipeline no app

O Airflow só orquestra: a DAG chama o app por HTTP (health check, dispara o pipeline, verifica o resultado). A lógica de ingestão, transformação e persistência vive no app FastAPI. Assim o pipeline é testável sem Airflow e pode ser versionado e deployado separado. O custo é perder o retry granular por etapa interna do pipeline. As alternativas seriam rodar o pandas num `PythonOperator` ou usar `KubernetesPodOperator`.

## LocalExecutor + Postgres

Parti do compose oficial do Airflow 3.2 e reduzi para LocalExecutor. O CeleryExecutor adicionaria Redis, workers e Flower sem ganho para uma DAG local. Abro mão da escala horizontal de workers, que não faz falta aqui.

## Kind em vez de Minikube

Kind é leve e é a mesma ferramenta usada no job de e2e do CI, então o ambiente local fica próximo do CI. Perco os addons e o dashboard do Minikube, que não fazem falta para este escopo.

## App no Kubernetes, Airflow no Compose

O desafio pede ao menos uma peça da stack no K8s. O chart do Airflow é pesado para um laptop e não demonstraria muito além de um helm install. Preferi usar o K8s no app, onde dá para mostrar probes, ConfigMap, resources e rollout. Em produção o Airflow também iria para o cluster.

## Comunicação Airflow para o app

O Airflow chama o app por `http://host.docker.internal:8000`, exposto por `kubectl port-forward` com `--address 0.0.0.0`. É a parte mais artificial do ambiente: em produção seria DNS de Service dentro do cluster. Aceitei essa cola para manter os dois mundos (Compose e Kind) simples e separados.

## Parquet em emptyDir

O resultado vai para um Parquet num volume emptyDir. O dado morre com o pod, e isso é proposital: o pipeline é idempotente (sobrescreve a cada run) e o objetivo é demonstrar o fluxo completo. Em produção seria object storage ou um warehouse.

## Imagem multi-stage

O primeiro estágio instala as dependências num venv com uv; o estágio final copia só o venv e o código, sem uv nem cache de build. A imagem caiu de ~1.07 GB para ~590 MB. O grosso do que sobra é pandas + pyarrow, que são parte da aplicação.

## CI

Lint (ruff pinado), testes de unidade do app, teste de integridade das DAGs (DagBag importa sem erros), kubeconform nos manifestos, build da imagem (push no GHCR só na main) e um e2e no Kind que deploya os manifestos reais e faz smoke test nos endpoints. O e2e custa alguns minutos por run, mas valida a cada PR o mesmo caminho da demo.

## Tooling

uv com lockfile por projeto (app e dags), para as dependências do app não se misturarem com as do Airflow, e ruff pinado no Makefile e no CI. Builds reprodutíveis local e no CI.

## Limitações conhecidas

- O contêiner roda como root (sem `runAsNonRoot` / `securityContext`).
- Sem gestão de segredos: o `.env` fica local. Em produção, um secrets manager.
- pandas pinado abaixo de 3.0 (a 3.0.4 foi retirada do PyPI por segfaults com datetime).
