# Scaling Open WebUI

Open WebUI follows a stateless, container-first architecture. Scaling it looks like scaling any modern web application.

## Understanding the Defaults

Out of the box, Open WebUI runs as a single container with:
- An embedded SQLite database stored on a local volume
- An embedded ChromaDB vector database (also backed by SQLite) for RAG embeddings
- A single Uvicorn worker process
- No external dependencies (no Redis, no external DB)

Both SQLite databases (main and vector) must be replaced before running multiple processes.

## Step 1: Switch to PostgreSQL

**When:** You plan to run more than one Open WebUI instance, or want better performance.

```
DATABASE_URL=postgresql://user:password@db-host:5432/openwebui
```

Key points:
- Open WebUI does not migrate data between databases -- plan before you have production data in SQLite.
- Tune `DATABASE_POOL_SIZE` and `DATABASE_POOL_MAX_OVERFLOW` to match usage. Good starting point: `DATABASE_POOL_SIZE=15` and `DATABASE_POOL_MAX_OVERFLOW=20`.
- Each Open WebUI instance maintains its own connection pool, so total connections = pool size x number of instances.
- Without PostgreSQL, multiple instances will cause `database is locked` errors and data corruption.

## Step 2: Add Redis

**When:** You want to run multiple Open WebUI instances or multiple Uvicorn workers.

```
REDIS_URL=redis://redis-host:6379/0
WEBSOCKET_MANAGER=redis
ENABLE_WEBSOCKET_SUPPORT=true
```

Key points:
- Not needed for single-instance deployments.
- For Redis Sentinel HA: also set `REDIS_SENTINEL_HOSTS` and consider `REDIS_SOCKET_CONNECT_TIMEOUT=5`.
- For AWS Elasticache or managed Redis Cluster: set `REDIS_CLUSTER=true`.
- Ensure Redis has `timeout 1800` and `maxclients` 10000+.
- A single Redis instance is sufficient for most deployments, even with thousands of users.
- Without Redis in multi-instance setup: WebSocket 403 errors, configuration sync issues, intermittent auth failures.

## Step 3: Run Multiple Instances

**When:** You need to handle more users or want high availability.

Before running multiple instances, complete Steps 1 and 2 (PostgreSQL and Redis). You also need a shared `WEBUI_SECRET_KEY` across all replicas.

### Option A: Container Orchestration (Recommended)

- Keep `UVICORN_WORKERS=1` per container
- Set `ENABLE_DB_MIGRATIONS=false` on all replicas except one "primary" pod
- Scale up/down by adjusting replica count

### Option B: Multiple Workers per Container

```
UVICORN_WORKERS=4
```

Spawns multiple processes inside a single container. Still needs PostgreSQL and Redis.

## Step 4: Switch to an External Vector Database

**When:** You run more than one Uvicorn worker or more than one replica. This is not optional.

The default ChromaDB uses a local PersistentClient backed by SQLite. SQLite connections are not fork-safe -- concurrent writes cause instant worker death.

```
VECTOR_DB=pgvector
```

| Vector DB | Best For | Configuration |
|---|---|---|
| **PGVector** | Teams already using PostgreSQL | `VECTOR_DB=pgvector` + `PGVECTOR_DB_URL=postgresql://...` |
| **MariaDB Vector** | HNSW-based vector search | `VECTOR_DB=mariadb-vector` + `MARIADB_VECTOR_DB_URL=mariadb+mariadbconnector://...` |
| **Milvus** | Large-scale self-hosted deployments | `VECTOR_DB=milvus` + `MILVUS_URI=http://milvus-host:19530` |
| **Qdrant** | Efficient filtering and metadata search | `VECTOR_DB=qdrant` + `QDRANT_URI=http://qdrant-host:6333` |
| **Pinecone** | Fully managed cloud service | `VECTOR_DB=pinecone` + `PINECONE_API_KEY=...` |
| **ChromaDB (HTTP mode)** | ChromaDB as separate server | `VECTOR_DB=chroma` + `CHROMA_HTTP_HOST=chroma-host` + `CHROMA_HTTP_PORT=8000` |

Only PGVector and ChromaDB will be consistently maintained by the Open WebUI team.

Milvus and Qdrant support multitenancy mode (`ENABLE_MILVUS_MULTITENANCY_MODE=True` / `ENABLE_QDRANT_MULTITENANCY_MODE=True`).
