# SPEC.md — Integration Engineering Platform

## 1. Project Overview

**Client:** wynwood tech Recruiting Team (for leading tech company in Germany)
**Project:** Integration Engineering Platform — workflow orchestration for cloud-native system integrations
**Goal:** Build a production-grade integration platform that connects enterprise systems via DAG-based workflows, deployed on Azure Kubernetes Service with support for Argo Workflows, Temporal, and Airflow
**Platform:** Upwork | **Budget:** Hourly (Expert, 30+ hrs/week) | **Duration:** 12+ months

---

## 2. Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION PLATFORM — AZURE AKS                       │
│                                                                          │◄── Azure Monitor / Application Insights
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────┐      │
│  │   REST API  │───►│  Task Queue  │───►│  Workflow Orchestrator │      │
│  │  (FastAPI)  │    │  (Redis)     │    │  (Argo WF / Temporal) │      │
│  └─────────────┘    └──────────────┘    └──────────┬───────────┘      │
│         │                   │                        │                   │
│         ▼                   ▼                        ▼                   │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────┐      │
│  │   Python    │    │  Scheduling  │    │   DAG Workflows        │      │
│  │  Workers    │    │  (APScheduler│    │   (Python DAGs)        │      │
│  │             │    │   cron/hours)│    │                        │      │
│  └──────┬──────┘    └──────────────┘    └──────────┬───────────┘      │
│         │                                            │                   │
│         ▼                                            ▼                   │
│  ┌──────────────────────────────────────────────────────────────┐        │
│  │                   CONNECTORS / ADAPTERS                      │        │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────┐│        │
│  │  │ Azure  │  │   DB   │  │  HTTP  │  │  File  │  │Event ││        │
│  │  │   SDK  │  │(SQL/NoS)│  │Webhook │  │  SFTP  │  │ Kafka││        │
│  │  └────────┘  └────────┘  └────────┘  └────────┘  └──────┘│        │
│  └──────────────────────────────────────────────────────────────┘        │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐        │
│  │              HERA SDK (Argo Workflows Python API)            │        │
│  │   @step decorator → Argo Workflow templates → AKS pod         │        │
│  └──────────────────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  PostgreSQL     │     │  Blob Storage    │
│  (workflow meta │     │  (Azure Blob)    │
│   + execution   │     │  artifacts       │
│   state)        │     │                  │
└─────────────────┘     └──────────────────┘
```

---

## 3. Core Workstreams

### Workstream 1: Workflow Orchestrator Selection & Integration
- **Primary engine:** Argo Workflows on AKS (Python-first via Hera SDK)
- **Secondary engine:** Temporal for long-running stateful workflows (compensation, saga patterns)
- **Scheduling layer:** Apache Airflow for cron-based DAG orchestration
- **Integration points:** All three share a common connector library

### Workstream 2: Python Integration Framework
- **Hera SDK:** Decorator-based workflow definitions (`@step`, `@ DAG`)
- **Connector interface:** Abstract base class for all integrations (Azure, DB, HTTP, File, Event)
- **Serialization:** Pydantic models for all task inputs/outputs
- **Error handling:** Retry with exponential backoff, dead-letter queues

### Workstream 3: Azure AKS Deployment
- **Cluster:** Azure Kubernetes Service with system/node pool separation
- **Helm charts:** Argo Workflows, Temporal, Redis (task queue), PostgreSQL
- **Autoscaling:** KEDA-based event-driven scaling for workflow workers
- **Networking:** Internal LoadBalancer, private endpoints for Azure resources
- **RBAC:** Service accounts per workflow namespace, least-privilege Azure AD integration

### Workstream 4: CI/CD Pipeline
- **Argo Events:** Trigger workflows from GitHub webhooks, Azure DevOps pipelines
- **GitHub Actions:** Lint → Unit tests → Integration tests → Helm chart publish
- **Container registry:** Azure Container Registry (ACR) with image scanning
- **GitOps:** Argo CD for declarative deployment to AKS

---

## 4. Data Model

### Workflow Definition
```
Workflow:
  id: UUID (PK)
  name: str
  engine: enum[argo, temporal, airflow]
  definition: JSON (DAG structure)
  created_at: timestamp
  updated_at: timestamp
  owner: str
  status: enum[active, paused, archived]

Task:
  id: UUID (PK)
  workflow_id: UUID (FK)
  name: str
  connector_type: enum[azure_sdk, db, http, file, event, custom]
  config: JSON (connector-specific config)
  retry_policy: JSON
  timeout_seconds: int

Execution:
  id: UUID (PK)
  workflow_id: UUID (FK)
  run_id: str (engine-specific run ID)
  status: enum[pending, running, succeeded, failed, cancelled]
  started_at: timestamp
  completed_at: timestamp
  inputs: JSON
  outputs: JSON
  error: str (nullable)
```

### Azure Resources
```
AzureSubscription:
  id: UUID (PK)
  tenant_id: str
  client_id: str (MSI or SP)
  subscription_id: str
  scope: str (scope for RBAC)

IntegrationConnector:
  id: UUID (PK)
  name: str
  type: enum[blob_storage, sql_db, service_bus, event_hub, key_vault, custom]
  config: JSON (encrypted at rest)
  azure_subscription_id: UUID (FK)
```

---

## 5. API Design

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflows` | Register new workflow (Argo/Temporal/Airflow) |
| GET | `/workflows` | List all workflows with status |
| GET | `/workflows/{id}` | Get workflow definition |
| POST | `/workflows/{id}/run` | Trigger workflow execution |
| GET | `/workflows/{id}/runs` | List execution history |
| GET | `/runs/{run_id}` | Get specific execution status/outputs |
| POST | `/workflows/{id}/pause` | Pause active workflow |
| POST | `/workflows/{id}/resume` | Resume paused workflow |
| POST | `/connectors` | Register new integration connector |
| GET | `/connectors` | List all connectors |
| POST | `/connectors/{id}/test` | Test connector connectivity |
| GET | `/health` | Health check (all engines) |

---

## 6. Technical Decisions

1. **Argo Workflows as primary** — Kubernetes-native, Python-first via Hera SDK, YAML-free workflow definitions, excellent Azure AKS integration
2. **Temporal for saga/compensation** — Long-running workflows with built-in activity heartbeats, retry semantics, and distributed transactions
3. **Airflow for cron orchestration** — Mature ecosystem, large operator library, used as schedule layer on top of Argo/Temporal task graph
4. **Hera SDK for Python DAGs** — `@step` decorator maps directly to Argo template steps; no YAML authoring for Python developers
5. **Redis for task queue** — Celery broker for Airflow; Temporal has its own task queue
6. **Azure Managed Identities** — No service principal secrets in config; MSI for AKS pods accessing Azure resources
7. **KEDA for autoscaling** — Event-driven scaling based on Redis queue depth / Argo workflow queue depth
8. **PostgreSQL for metadata** — Workflow definitions, execution history, audit log; Azure Database for PostgreSQL Flexible Server
9. **Azure Blob for artifacts** — Workflow input/output artifacts stored in Azure Blob with SAS token access
10. **Argo Events for webhooks** — Trigger workflows from GitHub, Azure DevOps, custom webhooks

---

## 7. Out of Scope

- Frontend UI / dashboard (API-only delivery)
- Multi-cloud deployment (Azure only)
- Non-Python language SDKs
- Legacy system connectors (SAP, Oracle EBS)
- Real-time streaming pipelines (Kafka-native only)

---

## 8. Success Metrics

- **Workflow execution:** 99.9% reliability for scheduled DAGs
- **Deployment:** Zero-downtime rolling updates via Argo CD
- **Latency:** Workflow trigger to first step execution < 5 seconds
- **Scale:** Handle 1000+ concurrent workflow executions on AKS
- **Developer experience:** New integration connector scaffolded and deployed < 1 hour
