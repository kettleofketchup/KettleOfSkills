# Deployment & Scaling Reference

## Installation

### Docker (Recommended)
```bash
# With Ollama on host
docker run -d -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui ghcr.io/open-webui/open-webui:main

# With bundled Ollama
docker run -d -p 3000:8080 \
  --gpus all \
  -v ollama:/root/.ollama \
  -v open-webui:/app/backend/data \
  --name open-webui ghcr.io/open-webui/open-webui:cuda

# OpenAI only
docker run -d -p 3000:8080 \
  -e ENABLE_OLLAMA_API=false \
  -e OPENAI_API_KEY=sk-xxx \
  --name open-webui ghcr.io/open-webui/open-webui:main

# pip
pip install open-webui && open-webui serve
```

### Updating
```bash
docker pull ghcr.io/open-webui/open-webui:main
docker stop open-webui && docker rm open-webui
# Re-run docker run with same volume mount
```

---

## Scaling (Multi-Instance)

### Required Steps

| Step | When Required |
|------|---------------|
| 1. PostgreSQL | Multiple instances OR better performance |
| 2. Redis | Multiple instances OR multiple workers |
| 3. External Vector DB | Multiple workers (ChromaDB not fork-safe) |
| 4. Shared Storage | Multiple instances needing file access |
| 5. External Extraction | Scale (prevents memory leaks) |

### Minimum Scaled Config
```bash
DATABASE_URL=postgresql://user:password@db:5432/openwebui
REDIS_URL=redis://redis:6379/0
WEBSOCKET_MANAGER=redis
ENABLE_WEBSOCKET_SUPPORT=true
VECTOR_DB=pgvector
PGVECTOR_DB_URL=postgresql://user:password@db:5432/openwebui
WEBUI_SECRET_KEY=shared-secret  # MUST be same across all replicas
UVICORN_WORKERS=1  # Let orchestrator scale
ENABLE_DB_MIGRATIONS=false  # Only one instance runs migrations
CONTENT_EXTRACTION_ENGINE=tika
TIKA_SERVER_URL=http://tika:9998
```

### Redis HA
```bash
REDIS_SENTINEL_HOSTS=sentinel:26379
# AWS ElastiCache:
REDIS_CLUSTER=true
```

### Cloud Storage
```bash
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=my-bucket
S3_REGION_NAME=us-east-1
```

### Scaling Decision Matrix

| Scenario | PostgreSQL | Redis | Ext. Vector DB |
|----------|:----------:|:-----:|:--------------:|
| Single user | - | - | - |
| Small team (<50) | Recommended | - | - |
| Multiple workers | Required | Required | Required |
| Multiple instances/HA | Required | Required | Required |

---

## Reverse Proxy

### Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 50M;  # File uploads

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_buffering off;          # Critical for SSE streaming
        proxy_cache off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
**Critical**: `proxy_buffering off` prevents garbled markdown/streaming corruption.

### Caddy
```
your-domain.com {
    reverse_proxy localhost:3000
}
```
Caddy handles SSE correctly by default.

---

## OpenTelemetry Monitoring

```bash
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
OTEL_SERVICE_NAME=open-webui
```

---

## Logging

```bash
GLOBAL_LOG_LEVEL=INFO
LOG_LEVEL=INFO                    # uvicorn level
SRC_LOG_LEVELS=RAG:DEBUG,MAIN:INFO  # Per-module
```

---

## Common Docker Networking

| Scenario | URL to Use |
|----------|-----------|
| Ollama on host (Linux) | `http://host.docker.internal:11434` or `--network=host` |
| Ollama on host (macOS) | `http://host.docker.internal:11434` |
| Ollama in Docker | `http://ollama:11434` (same network) |
| Podman on macOS | `http://host.containers.internal:11434` |

Set `OLLAMA_HOST=0.0.0.0` on Ollama to listen on all interfaces.
