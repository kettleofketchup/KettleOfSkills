# Open WebUI Environment Variables: Ollama, OpenAI, Database, Redis, WebSocket

## Ollama

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_OLLAMA_API` | bool | `True` | Enables Ollama APIs. PersistentConfig. |
| `OLLAMA_BASE_URL` | str | `http://localhost:11434` | Ollama backend URL. Docker: `http://host.docker.internal:11434`. K8s: `http://ollama-service.open-webui.svc.cluster.local:11434`. |
| `OLLAMA_BASE_URLS` | str | - | Load-balanced Ollama hosts (semicolon-separated). Takes precedence over `OLLAMA_BASE_URL`. PersistentConfig. |
| `USE_OLLAMA_DOCKER` | bool | `False` | Bundles Ollama instance in Docker image. |
| `K8S_FLAG` | bool | `False` | Assumes Helm deployment, sets Ollama URL to K8s service. |

## OpenAI

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_OPENAI_API` | bool | `True` | Enables OpenAI APIs. PersistentConfig. |
| `OPENAI_API_BASE_URL` | str | `https://api.openai.com/v1` | OpenAI base URL. PersistentConfig. |
| `OPENAI_API_BASE_URLS` | str | - | Multiple OpenAI base URLs (semicolon-separated). PersistentConfig. |
| `OPENAI_API_KEY` | str | - | OpenAI API key. PersistentConfig. |
| `OPENAI_API_KEYS` | str | - | Multiple API keys (semicolon-separated). PersistentConfig. |

## Database

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | str | SQLite default | Database connection string. PostgreSQL required for multi-replica. Example: `postgresql://user:password@host:5432/openwebui`. |
| `DATABASE_POOL_SIZE` | int | SQLAlchemy default | Connection pool size. Increase for high concurrency. |
| `DATABASE_POOL_MAX_OVERFLOW` | int | `0` | Max connections beyond pool size. Combined total should stay under DB `max_connections`. |
| `DATABASE_ENABLE_SESSION_SHARING` | bool | `False` | Reuses DB sessions. Enable for PostgreSQL with adequate resources. Keep disabled for SQLite/low-spec hardware. |
| `ENABLE_DB_MIGRATIONS` | bool | `True` | Automatic DB migrations on startup. Set `False` on non-master replicas. |

**Pool sizing formula:** `Total connections = (POOL_SIZE + MAX_OVERFLOW) x (replicas x UVICORN_WORKERS)`

## Redis & WebSocket

| Variable | Type | Default | Description |
|---|---|---|---|
| `REDIS_URL` | str | - | Redis URL for config sync via Pub/Sub. Example: `redis://redis:6379/0`. |
| `ENABLE_WEBSOCKET_SUPPORT` | bool | `True` | Enables WebSocket support. Required for v0.5.0+. |
| `WEBSOCKET_MANAGER` | str | - | Set to `redis` for multi-instance. |
| `WEBSOCKET_REDIS_URL` | str | - | Redis URL for WebSocket management. Example: `redis://redis:6379/1`. |

## Direct Connections (OpenAPI/MCPO Tool Servers)

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_DIRECT_CONNECTIONS` | bool | `True` | Enables direct connections. PersistentConfig. |
| `TOOL_SERVER_CONNECTIONS` | str (JSON) | `[]` | JSON array of tool server connection configs. PersistentConfig. |

Example:
```json
[{"type":"openapi","url":"example-url","spec_type":"url","spec":"","path":"openapi.json","auth_type":"none","key":"","config":{"enable":true},"info":{"id":"","name":"example-server","description":"MCP server."}}]
```

## Terminal Server

| Variable | Type | Default | Description |
|---|---|---|---|
| `TERMINAL_SERVER_CONNECTIONS` | str (JSON) | `[]` | JSON array of terminal server configs. Admin-configured, proxied through Open WebUI. PersistentConfig. |

## Vector Database

| Variable | Type | Default | Description |
|---|---|---|---|
| `VECTOR_DB` | str | `chroma` | Vector DB: `chroma`, `elasticsearch`, `mariadb-vector`, `milvus`, `opensearch`, `pgvector`, `qdrant`, `pinecone`, `s3vector`, `oracle23ai`, `weaviate`. |

**ChromaDB (default) is NOT safe for multi-worker/multi-replica.** SQLite connections are not fork-safe. Switch to pgvector, milvus, qdrant, or run ChromaDB as HTTP server.

### ChromaDB

| Variable | Type | Default | Description |
|---|---|---|---|
| `CHROMA_HTTP_HOST` | str | - | Remote ChromaDB hostname. Required for multi-worker. |
| `CHROMA_HTTP_PORT` | int | `8000` | Remote ChromaDB port. |
| `CHROMA_HTTP_HEADERS` | str | - | Comma-separated HTTP headers. |
| `CHROMA_HTTP_SSL` | bool | `False` | SSL for ChromaDB connections. |
| `CHROMA_CLIENT_AUTH_PROVIDER` | str | - | Auth provider for remote ChromaDB. |
| `CHROMA_CLIENT_AUTH_CREDENTIALS` | str | - | Auth credentials (`username:password`). |
| `CHROMA_TENANT` | str | default | ChromaDB tenant. |
| `CHROMA_DATABASE` | str | default | ChromaDB database. |

### PGVector

| Variable | Type | Default | Description |
|---|---|---|---|
| `PGVECTOR_DB_URL` | str | `$DATABASE_URL` | PGVector database URL. |
| `PGVECTOR_INITIALIZE_MAX_VECTOR_LENGTH` | str | `1536` | Max vector length. |
| `PGVECTOR_CREATE_EXTENSION` | str | `true` | Auto-create vector extension. Set `false` for non-superuser. |
| `PGVECTOR_INDEX_METHOD` | str | - | Index method: `ivfflat`, `hnsw`. PersistentConfig. |
| `PGVECTOR_HNSW_M` | int | `16` | HNSW connections per layer. PersistentConfig. |
| `PGVECTOR_HNSW_EF_CONSTRUCTION` | int | `64` | HNSW candidate list size. PersistentConfig. |
| `PGVECTOR_IVFFLAT_LISTS` | int | `100` | IVFFlat cluster count. PersistentConfig. |
| `PGVECTOR_USE_HALFVEC` | bool | `False` | Use halfvec for >2000 dimensions. |
| `PGVECTOR_POOL_SIZE` | int | `None` | Connection pool size. |
| `PGVECTOR_POOL_MAX_OVERFLOW` | int | `0` | Max overflow connections. |
| `PGVECTOR_POOL_TIMEOUT` | int | `30` | Pool connection timeout (seconds). |
| `PGVECTOR_POOL_RECYCLE` | int | `3600` | Connection recycle time (seconds). |

### Qdrant

| Variable | Type | Default | Description |
|---|---|---|---|
| `QDRANT_URI` | str | - | Qdrant URI. |
| `QDRANT_API_KEY` | str | - | Qdrant API key. |
| `QDRANT_ON_DISK` | bool | `False` | Enable memmap storage. |
| `QDRANT_PREFER_GRPC` | bool | `False` | Use gRPC interface. |
| `QDRANT_GRPC_PORT` | int | `6334` | gRPC port. |
| `QDRANT_TIMEOUT` | int | `5` | Request timeout (seconds). |
| `ENABLE_QDRANT_MULTITENANCY_MODE` | bool | `True` | Consolidates collections for RAM savings. |
| `QDRANT_COLLECTION_PREFIX` | str | `open-webui` | Collection name prefix. |

### Milvus

| Variable | Type | Default | Description |
|---|---|---|---|
| `MILVUS_URI` | str | `${DATA_DIR}/vector_db/milvus.db` | Milvus connection URI. |
| `MILVUS_TOKEN` | str | `None` | Auth token (`username:password`). |
| `MILVUS_INDEX_TYPE` | str | `HNSW` | Index: `AUTOINDEX`, `FLAT`, `IVF_FLAT`, `HNSW`, `DISKANN`. |
| `MILVUS_METRIC_TYPE` | str | `COSINE` | Similarity metric: `COSINE`, `IP`, `L2`. |
| `ENABLE_MILVUS_MULTITENANCY_MODE` | bool | `false` | Consolidates to 5 shared collections. |
| `MILVUS_COLLECTION_PREFIX` | str | `open_webui` | Collection prefix (underscores only). |

### Elasticsearch / OpenSearch / Pinecone / Weaviate / MariaDB Vector / Oracle / S3

See the full env-configuration documentation for these providers. Key variables follow the pattern: `{PROVIDER}_URL`, `{PROVIDER}_API_KEY`, `{PROVIDER}_USERNAME`, `{PROVIDER}_PASSWORD`.
