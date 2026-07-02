# Decisões técnicas

O que escolhi, o que abri mão e por quê.

## DAG fina, pipeline no app

O Airflow só orquestra: a DAG chama o app por HTTP (health check, dispara o pipeline, verifica o resultado). A lógica de ingestão, transformação e persistência vive no app FastAPI. Assim o pipeline é testável sem Airflow e pode ser versionado e deployado separado. O custo é perder o retry granular por etapa interna do pipeline. As alternativas seriam rodar o pandas num `PythonOperator` ou usar `KubernetesPodOperator`.

## LocalExecutor em vez de CeleryExecutor

Parti do compose oficial do Airflow 3.2 e reduzi para LocalExecutor. O CeleryExecutor adicionaria Redis, workers e Flower sem ganho para uma DAG local. Abro mão da escala horizontal de workers, que não faz falta aqui.

## Kind em vez de Minikube

Kind é leve e é a mesma ferramenta usada no job de e2e do CI, então o ambiente local valida igual ao CI. Abro mão dos addons do Minikube (dashboard, metrics-server, tunnel para LoadBalancer), que não fazem falta para este escopo.

## App no Kubernetes, Airflow no Compose

O desafio pede ao menos uma peça da stack no K8s. O chart do Airflow é pesado para um laptop e não demonstraria muito além de um helm install. Preferi usar o K8s no app, onde dá para mostrar probes, ConfigMap, resources e rollout. Em produção o Airflow também iria para o cluster.

## Comunicação Airflow para o app via host

O Airflow chama o app por `http://host.docker.internal:8000`, exposto por `kubectl port-forward` com `--address 0.0.0.0`. É a parte mais artificial do ambiente: em produção seria DNS de Service dentro do cluster. Aceitei essa cola para manter os dois mundos (Compose e Kind) simples e separados.

## Parquet em emptyDir

O resultado vai para um Parquet num volume emptyDir. O dado morre com o pod, e isso é proposital: o pipeline é idempotente (sobrescreve a cada run) e o objetivo é demonstrar o fluxo completo. Em produção seria object storage ou um warehouse. Um PVC (PersistentVolumeClaim) não resolveria o caso com réplicas (access mode ReadWriteOnce) e adicionaria estado sem necessidade. RWX (ReadWriteMany) existe, mas necessitaria de network storage como NFS, o que é complexo e overkill para dados temporários na demo.

## E2E no Kind dentro do CI

Além de lint, testes e validação de manifestos, o CI sobe um cluster Kind, deploya os manifestos reais e faz smoke test nos endpoints. Custa alguns minutos por run, mas garante que o mesmo caminho da demo (build, load, apply, curl) passa a cada PR. A alternativa barata seria parar nos testes de unidade e confiar que os manifestos válidos funcionam juntos.

## Limitações conhecidas

- O contêiner roda como root (sem `runAsNonRoot` / `securityContext`).
- Sem gestão de segredos: o `.env` fica local. Em produção, um secrets manager.
- pandas pinado abaixo de 3.0 (a 3.0.4 foi retirada do PyPI por segfaults com datetime).
