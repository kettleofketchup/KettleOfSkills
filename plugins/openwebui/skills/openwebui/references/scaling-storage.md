# Scaling Open WebUI - Storage, Extraction, and Observability

## Step 5: Share File Storage Across Instances

**When:** Running multiple instances that need to share uploaded files, images, and user data.

By default, files are stored on the local filesystem under `DATA_DIR` (typically `/app/backend/data`).

`STORAGE_PROVIDER` only controls where uploaded files are stored. It does not affect the main database (`DATABASE_URL`) or vector database (`VECTOR_DB`).

### Option A: Shared Filesystem (Simplest)

No configuration changes needed -- just ensure all instances mount the same directory.

**Kubernetes:**
```yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: openwebui-data  # Must be ReadWriteMany (RWX)
```

**Docker Compose:**
```yaml
volumes:
  - /opt/data/openwebui-data:/app/backend/data
```

Do not store the SQLite database on a network filesystem. SQLite's file locking does not work reliably over NFS.

### Option B: Cloud Object Storage

| Provider | Set `STORAGE_PROVIDER` to |
|---|---|
| Amazon S3 (or S3-compatible like MinIO, R2) | `s3` |
| Google Cloud Storage | `gcs` |
| Microsoft Azure Blob Storage | `azure` |

```
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=my-openwebui-bucket
S3_REGION_NAME=us-east-1
```

## Step 6: Fix Content Extraction and Embeddings

**When:** Processing documents regularly (RAG, knowledge bases) in production.

Default content extraction (pypdf) and embedding engine (SentenceTransformers) are the two most common causes of memory leaks in production.

### Switch Content Extraction Engine

```
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998
```

The default extractor (pypdf) has known memory leaks. External extractors (Tika, Docling) run in their own container, isolating leaks.

### Switch Embedding Engine

```
RAG_EMBEDDING_ENGINE=openai
# or for self-hosted:
RAG_EMBEDDING_ENGINE=ollama
```

Default SentenceTransformers loads ~500MB per worker process. With 8 workers = 4GB RAM for embeddings.

## Step 7: Add Observability

Open WebUI supports OpenTelemetry for traces, metrics, and logs:

```
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317
```

## Production Architecture

```
         Load Balancer (Nginx, HAProxy, Cloud LB)
              |          |          |
         WebUI Pod 1  Pod 2     Pod N   (Stateless containers)
              |          |          |
         PostgreSQL (+ PGVector for RAG)
         Redis (Shared state & websockets)
         Shared Storage (NFS or S3)
```

## Minimum Environment Variables for Scaled Deployments

```bash
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

# Workers
UVICORN_WORKERS=1

# Migrations (set to false on all but one instance)
ENABLE_DB_MIGRATIONS=false
```

## Quick Reference: When Do I Need What?

| Scenario | PostgreSQL | Redis | External Vector DB | Ext. Content Extraction | Ext. Embeddings | Shared Storage |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Single user / evaluation | No | No | No | No | No | No |
| Small team (< 50 users) | Recommended | No | No | Recommended | No | No |
| Multiple Uvicorn workers | Required | Required | Required | Strongly Recommended | Strongly Recommended | No |
| Multiple instances / HA | Required | Required | Required | Strongly Recommended | Strongly Recommended | Optional (NFS or S3) |
| Large scale (1000+ users) | Required | Required | Required | Strongly Recommended | Strongly Recommended | Optional (NFS or S3) |
