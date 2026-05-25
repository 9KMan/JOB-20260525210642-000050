# Integration Engineering Platform

Production-grade integration platform connecting enterprise systems via DAG-based workflows, deployed on Azure Kubernetes Service with support for Argo Workflows, Temporal, and Airflow.

## Architecture

- **REST API**: FastAPI on Azure AKS
- **Task Queue**: Redis
- **Workflow Engines**: Argo Workflows (primary), Temporal (saga/compensation), Airflow (cron scheduling)
- **Connectors**: Azure SDK, DB, HTTP, File, Event
- **Python SDK**: Hera for Argo Workflows

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python -m src.main

# Run with uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflows` | Register new workflow |
| GET | `/workflows` | List all workflows |
| GET | `/workflows/{id}` | Get workflow definition |
| POST | `/workflows/{id}/run` | Trigger workflow execution |
| GET | `/workflows/{id}/runs` | List execution history |
| GET | `/runs/{run_id}` | Get execution status |
| POST | `/workflows/{id}/pause` | Pause workflow |
| POST | `/workflows/{id}/resume` | Resume workflow |
| POST | `/connectors` | Register connector |
| GET | `/connectors` | List connectors |
| POST | `/connectors/{id}/test` | Test connector |
| GET | `/health` | Health check |

## Deployment

```bash
# Deploy to AKS via Helm
helm install integration-platform ./helm/argo-workflows

# Deploy via Argo CD
argocd app create integration-platform --repo <repo> --path ./k8s --dest-server https://kubernetes.default.svc
```

## License

MIT