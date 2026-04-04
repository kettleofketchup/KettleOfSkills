# Scalable Enterprise Deployment Options

Open WebUI's **stateless, container-first architecture** means the same application runs identically whether you deploy it as a Python process on a VM, a container in a managed service, or a pod in a Kubernetes cluster. The difference between deployment patterns is how you **orchestrate, scale, and operate** the application.

How you serve LLM models is separate from how you deploy Open WebUI. You can use **managed APIs** (OpenAI, Anthropic, Azure OpenAI, Google Gemini) or **self-hosted inference** (Ollama, vLLM) with any deployment pattern.

---

## Shared Infrastructure Requirements

Every scaled Open WebUI deployment requires the same set of backing services. Configure these **before** scaling beyond a single instance.

| Component | Why It's Required | Options |
| :--- | :--- | :--- |
| **PostgreSQL** | Multi-instance deployments require a real database. SQLite does not support concurrent writes from multiple processes. | Self-managed, Amazon RDS, Azure Database for PostgreSQL, Google Cloud SQL |
| **Redis** | Session management, WebSocket coordination, and configuration sync across instances. | Self-managed, Amazon ElastiCache, Azure Cache for Redis, Google Memorystore |
| **Vector Database** | The default ChromaDB uses a local SQLite backend that is not safe for multi-process access. | PGVector (shares PostgreSQL), Milvus, Qdrant, or ChromaDB in HTTP server mode |
| **Shared Storage** | Uploaded files must be accessible from every instance. | Shared filesystem (NFS, EFS, CephFS) or object storage (`S3`, `GCS`, `Azure Blob`) |
| **Content Extraction** | The default `pypdf` extractor leaks memory under sustained load. | Apache Tika or Docling as a sidecar service |
| **Embedding Engine** | The default SentenceTransformers model loads ~500 MB into RAM per worker process. | OpenAI Embeddings API, or Ollama running an embedding model |

### Critical Configuration

These environment variables **must** be set consistently across every instance:

```bash
# Shared secret -- MUST be identical on all instances
WEBUI_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui

# Vector Database
VECTOR_DB=pgvector
PGVECTOR_DB_URL=postgresql://user:password@db-host:5432/openwebui

# Redis
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis
ENABLE_WEBSOCKET_SUPPORT=true

# Content Extraction
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998

# Embeddings
RAG_EMBEDDING_ENGINE=openai

# Storage -- choose ONE:
# Option A: shared filesystem (mount the same volume to all instances, no env var needed)
# Option B: object storage
# STORAGE_PROVIDER=s3

# Workers -- let the orchestrator handle scaling
UVICORN_WORKERS=1

# Migrations -- only ONE instance should run migrations
ENABLE_DB_MIGRATIONS=false
```

**Database Migrations:** Set `ENABLE_DB_MIGRATIONS=false` on **all instances except one**. During updates, scale down to a single instance, allow migrations to complete, then scale back up. Concurrent migrations can corrupt your database.

---

## Deployment Comparison

| | **Python / Pip (VMs)** | **Container Service** | **Kubernetes (Helm)** |
| :--- | :--- | :--- | :--- |
| **Operational complexity** | Moderate -- OS patching, Python management | Low -- platform-managed containers | Higher -- requires K8s expertise |
| **Auto-scaling** | Cloud ASG/VMSS with health checks | Platform-native, minimal configuration | HPA with fine-grained control |
| **Container isolation** | None -- process runs directly on OS | Full container isolation | Full container + namespace isolation |
| **Rolling updates** | Manual (scale down, update, scale up) | Platform-managed rolling deployments | Declarative rolling updates with rollback |
| **Infrastructure-as-code** | Terraform/Pulumi for VMs + config mgmt | Task/service definitions (CloudFormation, Bicep, Terraform) | Helm charts + GitOps (Argo CD, Flux) |
| **Best suited for** | Teams with VM-centric operations, regulatory constraints | Teams wanting container benefits without K8s complexity | Large-scale, mission-critical deployments |
| **Minimum team expertise** | Linux administration, Python | Container fundamentals, cloud platform | Kubernetes, Helm, cloud-native patterns |

---

## Observability

### Health Checks

- **`/health`** -- Basic liveness check. Returns HTTP 200 when the application is running.
- **`/api/models`** -- Verifies the application can connect to configured model backends. Requires an API key.

### OpenTelemetry

```bash
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4318
OTEL_SERVICE_NAME=open-webui
```

This auto-instruments FastAPI, SQLAlchemy, Redis, and HTTP clients.

### Structured Logging

```bash
LOG_FORMAT=json
GLOBAL_LOG_LEVEL=INFO
```
