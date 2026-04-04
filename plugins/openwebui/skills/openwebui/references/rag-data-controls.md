# RAG, Data Controls, Memory & Direct Connections Reference

## RAG Configuration

### Core Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_TOP_K` | `3` | Top results from vector search |
| `RAG_TOP_K_RERANKER` | `3` | Reranker result count |
| `RAG_RELEVANCE_THRESHOLD` | `0.0` | Minimum similarity score |
| `RAG_CHUNK_SIZE` | `1500` | Max chars/tokens per chunk |
| `RAG_CHUNK_OVERLAP` | `100` | Shared content between chunks |
| `RAG_TEMPLATE` | `''` | Custom RAG prompt template |
| `RAG_SYSTEM_PROMPT` | `''` | System message for RAG ops |
| `RAG_SYSTEM_CONTEXT` | `False` | Inject RAG into system msg (enables KV cache) |
| `RAG_FULL_CONTEXT` | `False` | Return complete documents vs chunks |
| `RAG_HYBRID_BM25_WEIGHT` | `0.5` | Balance semantic vs BM25 (0=semantic, 1=BM25) |
| `ENABLE_RAG_HYBRID_SEARCH` | `False` | Combined vector + BM25 retrieval |
| `BYPASS_EMBEDDING_AND_RETRIEVAL` | `False` | Skip RAG pipeline entirely |

### Embedding Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_EMBEDDING_ENGINE` | `''` | Provider (Ollama, OpenAI, etc.) |
| `RAG_EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `RAG_EMBEDDING_BATCH_SIZE` | `1` | Embeddings per batch |
| `RAG_EMBEDDING_QUERY_PREFIX` | `None` | Prepended to search queries |
| `RAG_EMBEDDING_CONTENT_PREFIX` | `None` | Prepended to documents |
| `RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE` | `False` | Allow custom Hub models |

### Reranking

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_RERANKING_ENGINE` | `''` | Reranking provider |
| `RAG_RERANKING_MODEL` | `''` | Reranking model name |

### File Upload & Processing

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_FILE_MAX_COUNT` | `None` | Max files per KB |
| `RAG_FILE_MAX_SIZE` | `None` | File size limit (bytes) |
| `UPLOAD_DIR` | `{DATA_DIR}/uploads` | Upload storage dir |
| `PDF_EXTRACT_IMAGES` | `False` | Extract images from PDFs |

### KV Cache Optimization
`RAG_SYSTEM_CONTEXT=True` injects context into system messages for provider caching. Recommended for Ollama, llama.cpp, OpenAI, Vertex AI.

### Critical: Ollama Context Length
Ollama defaults to **2048-token** context -- set to **8192+** (preferably **16,000+**) via Admin Panel > Models > Settings > Advanced Parameters.

---

## Vector Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VECTOR_DB` | `chroma` | Backend: `chroma`, `elasticsearch`, `milvus`, `opensearch`, `pgvector`, `qdrant`, `pinecone`, `weaviate`, `mariadb-vector`, `oracle23ai`, `s3vector` |

### ChromaDB
| Variable | Description |
|----------|-------------|
| `CHROMA_HTTP_HOST` | Remote hostname (required for multi-worker) |
| `CHROMA_HTTP_PORT` | Port (default: 8000) |
| `CHROMA_HTTP_SSL` | SSL toggle |

### Milvus
| Variable | Description |
|----------|-------------|
| `MILVUS_URI` | Connection URI |
| `MILVUS_INDEX_TYPE` | `AUTOINDEX`, `FLAT`, `IVF_FLAT`, `HNSW`, `DISKANN` |

### PGVector
`PGVECTOR_DB_URL` -- PostgreSQL connection string (required)

### Qdrant
`QDRANT_URI` + optional `QDRANT_API_KEY`

### Elasticsearch
`ELASTICSEARCH_URL`, `ELASTICSEARCH_USERNAME`, `ELASTICSEARCH_PASSWORD`, `ELASTICSEARCH_API_KEY`

---

## Document Extraction

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTENT_EXTRACTION_ENGINE` | `''` | `''` (default), `tika`, `docling`, `mistral` |

### Apache Tika
```yaml
services:
  tika:
    image: apache/tika:latest-full
    ports: ["9998:9998"]
```
`TIKA_SERVER_URL` = `http://tika:9998`

### Docling
```yaml
services:
  docling-serve:
    image: quay.io/docling-project/docling-serve-cu128:latest
    ports: ["5001:5001"]
    environment:
      - UVICORN_WORKERS=1  # Must be 1
      - DOCLING_SERVE_ENABLE_UI=true
```

Parameters: `pdf_backend` (`dlparse_v1`/`v2`/`v4`), `table_mode` (`fast`/`accurate`), `ocr_engine` (`tesseract`/`easyocr`/`rapidocr`), `pipeline` (`standard`/`fast`)

### Mistral OCR
Get API key from console.mistral.ai > Admin Panel > Settings > Documents > "Mistral OCR"

---

## Data Controls

### Import/Export
- Export: JSON with all messages, metadata, timestamps
- Import: Open WebUI JSON, ChatGPT exports (auto-detected), custom JSON
- ChatGPT auto-detected when first object contains `mapping` key

### JSON Schema (Standard Format)
```json
[{
  "chat": {
    "title": "...",
    "models": ["llama3.2"],
    "history": {
      "currentId": "msg-2",
      "messages": {
        "msg-1": {"id": "msg-1", "parentId": null, "childrenIds": ["msg-2"], "role": "user", "content": "..."},
        "msg-2": {"id": "msg-2", "parentId": "msg-1", "childrenIds": [], "role": "assistant", "content": "...", "model": "llama3.2", "done": true}
      }
    }
  }
}]
```
Messages use tree structure (parent/child) supporting branching conversations.

---

## Memory & Personalization

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_MEMORIES` | `True` | Global toggle |
| `USER_PERMISSIONS_FEATURES_MEMORIES` | `True` | Role/group access |

### Native Memory Tools (Agentic Mode)
`add_memory`, `search_memories`, `replace_memory_content`, `delete_memory`, `list_memories`

Requires Native Function Calling + frontier models.

---

## Direct Connections

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_DIRECT_CONNECTIONS` | `True` | Enable browser-to-provider direct comms |

API keys stored in browser localStorage. Provider must have CORS configured.

---

## Google Drive & YouTube

| Variable | Description |
|----------|-------------|
| `ENABLE_GOOGLE_DRIVE_INTEGRATION` | Enable Drive file access |
| `GOOGLE_DRIVE_CLIENT_ID` | OAuth 2.0 client ID |
| `GOOGLE_DRIVE_API_KEY` | API key |
| `YOUTUBE_API_KEY` | YouTube data API key |
