# Open WebUI API Endpoints

## Authentication

Authenticate using Bearer Token from **Settings > Account** or JWT. Set `ENV=dev` for Swagger docs at `/docs`.

## Chat Completions (OpenAI-Compatible)

**POST** `/api/chat/completions` -- Works with Ollama, OpenAI, and Function models.

```bash
curl -X POST http://localhost:3000/api/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.1", "messages": [{"role": "user", "content": "Why is the sky blue?"}]}'
```

## Anthropic Messages API

**POST** `/api/v1/messages` or `/api/message` -- Anthropic-compatible. Supports `Authorization: Bearer` and `x-api-key` headers. Both streaming and non-streaming. Tool use supported.

```bash
curl -X POST http://localhost:3000/api/v1/messages \
  -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'
```

**Python (Anthropic SDK):** `base_url` must be `http://localhost:3000/api` (SDK appends `/v1/messages`).

**Claude Code:** Set `ANTHROPIC_BASE_URL=http://localhost:3000/api` and `ANTHROPIC_API_KEY=YOUR_KEY`.

## Models

**GET** `/api/models` -- List all models.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:3000/api/models
```

## Filter Behavior with API

| Filter | WebUI | Direct API |
|--------|-------|-----------|
| `inlet()` | Runs | Runs |
| `stream()` | Runs | Runs |
| `outlet()` | Runs | Does NOT run |

To trigger outlet processing for direct API: **POST** `/api/chat/completed` with model, messages, optional chat_id.

## Ollama API Proxy

**Base URL:** `/ollama/<api>` -- Transparent passthrough to native Ollama API.

- Generate: `POST /ollama/api/generate`
- List models: `GET /ollama/api/tags`
- Embeddings: `POST /ollama/api/embed`

Must include `Content-Type: application/json` for POST requests.

## RAG - File Upload & Knowledge

### Upload Files

**POST** `/api/v1/files/` -- Query params: `process` (bool, default true), `process_in_background` (bool, default true).

```bash
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" -H "Accept: application/json" \
  -F "file=@/path/to/file" http://localhost:3000/api/v1/files/
```

Files are processed **asynchronously** by default. You must wait for processing to complete before adding to knowledge bases.

### Check Processing Status

**GET** `/api/v1/files/{id}/process/status` -- Query param: `stream` (bool). Status values: `pending`, `completed`, `failed`.

### Add File to Knowledge

**POST** `/api/v1/knowledge/{id}/file/add` -- Body: `{"file_id": "your-file-id"}`. Always verify file status is `completed` first.

### Process Web URL

**POST** `/api/v1/retrieval/process/web` -- Query params: `process` (bool), `overwrite` (bool, default true). Body: `{"url": "...", "collection_name": "..."}`.

### Use Files in Chat

Include `files` array in chat completions:

```json
{"model": "gpt-4-turbo", "messages": [...], "files": [{"type": "file", "id": "file-id"}]}
```

For knowledge collections: `{"type": "collection", "id": "collection-id"}`.

## Complete Workflow Example

```python
import requests, time

WEBUI_URL = 'http://localhost:3000'
TOKEN = 'your-api-key'
headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/json'}

# 1. Upload
with open('doc.pdf', 'rb') as f:
    resp = requests.post(f'{WEBUI_URL}/api/v1/files/', headers=headers, files={'file': f})
file_id = resp.json()['id']

# 2. Wait for processing
while True:
    status = requests.get(f'{WEBUI_URL}/api/v1/files/{file_id}/process/status', headers=headers).json()
    if status['status'] == 'completed': break
    if status['status'] == 'failed': raise Exception(status.get('error'))
    time.sleep(2)

# 3. Add to knowledge base
requests.post(f'{WEBUI_URL}/api/v1/knowledge/{knowledge_id}/file/add',
    headers={**headers, 'Content-Type': 'application/json'}, json={'file_id': file_id})
```
