# Open WebUI Environment Variables: Tasks, Code Execution, Permissions

## Tasks

| Variable | Type | Default | Description |
|---|---|---|---|
| `TASK_MODEL` | str | - | Default task model for Ollama (title/tag/query generation). PersistentConfig. |
| `TASK_MODEL_EXTERNAL` | str | - | Default task model for OpenAI-compatible endpoints. PersistentConfig. |
| `ENABLE_TITLE_GENERATION` | bool | `True` | Chat title generation. PersistentConfig. |
| `TITLE_GENERATION_PROMPT_TEMPLATE` | str | default | Title generation prompt. PersistentConfig. |
| `ENABLE_FOLLOW_UP_GENERATION` | bool | `True` | Follow-up question generation. PersistentConfig. |
| `FOLLOW_UP_GENERATION_PROMPT_TEMPLATE` | str | default | Follow-up prompt template. PersistentConfig. |
| `ENABLE_TAGS_GENERATION` | bool | `True` | Tag generation. PersistentConfig. |
| `TAGS_GENERATION_PROMPT_TEMPLATE` | str | default | Tag generation prompt. PersistentConfig. |
| `TOOLS_FUNCTION_CALLING_PROMPT_TEMPLATE` | str | default | Tool calling prompt. PersistentConfig. |
| `ENABLE_SEARCH_QUERY_GENERATION` | bool | `True` | Search query generation. PersistentConfig. |
| `QUERY_GENERATION_PROMPT_TEMPLATE` | str | default | Query generation prompt. PersistentConfig. |

## Code Execution

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_CODE_EXECUTION` | bool | `True` | Enables code execution. PersistentConfig. |
| `CODE_EXECUTION_ENGINE` | str | `pyodide` | Code execution engine. PersistentConfig. |
| `CODE_EXECUTION_JUPYTER_URL` | str | `None` | Jupyter URL for code execution. PersistentConfig. |
| `CODE_EXECUTION_JUPYTER_AUTH` | str | `None` | Jupyter auth method. PersistentConfig. |
| `CODE_EXECUTION_JUPYTER_AUTH_TOKEN` | str | `None` | Jupyter auth token. PersistentConfig. |
| `CODE_EXECUTION_JUPYTER_AUTH_PASSWORD` | str | `None` | Jupyter auth password. PersistentConfig. |
| `CODE_EXECUTION_JUPYTER_TIMEOUT` | str | `None` | Jupyter execution timeout. PersistentConfig. |

## Code Interpreter

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_CODE_INTERPRETER` | bool | `True` | Enables code interpreter. PersistentConfig. |
| `CODE_INTERPRETER_ENGINE` | str | `pyodide` | Code interpreter engine. PersistentConfig. |
| `CODE_INTERPRETER_BLACKLISTED_MODULES` | str | `None` | Comma-separated blacklisted Python modules. |
| `CODE_INTERPRETER_PROMPT_TEMPLATE` | str | `None` | Code interpreter prompt. PersistentConfig. |
| `CODE_INTERPRETER_JUPYTER_URL` | str | `None` | Jupyter URL. PersistentConfig. |
| `CODE_INTERPRETER_JUPYTER_AUTH` | str | `None` | Jupyter auth method. PersistentConfig. |
| `CODE_INTERPRETER_JUPYTER_AUTH_TOKEN` | str | `None` | Jupyter auth token. PersistentConfig. |
| `CODE_INTERPRETER_JUPYTER_AUTH_PASSWORD` | str | `None` | Jupyter auth password. PersistentConfig. |
| `CODE_INTERPRETER_JUPYTER_TIMEOUT` | str | `None` | Jupyter timeout. PersistentConfig. |

## Autocomplete

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_AUTOCOMPLETE_GENERATION` | bool | `True` | Enables autocomplete. High impact on resources -- triggers on every keystroke. PersistentConfig. |
| `AUTOCOMPLETE_GENERATION_INPUT_MAX_LENGTH` | int | `-1` | Max input length for autocomplete. PersistentConfig. |
| `AUTOCOMPLETE_GENERATION_PROMPT_TEMPLATE` | str | default | Autocomplete prompt template. PersistentConfig. |

## Pip Install & Functions

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS` | bool | `True` | Runtime pip installs from function frontmatter. Set `False` for multi-worker. |
| `EXTRA_PIP_PACKAGES` | str | - | Extra pip packages to install on container start. |

## Performance Profiles

### Weak Hardware (Raspberry Pi, <4GB RAM)
- `AUDIO_STT_ENGINE=webapi` (zero server load)
- `ENABLE_IMAGE_GENERATION=False`
- `ENABLE_CODE_INTERPRETER=False`
- `ENABLE_AUTOCOMPLETE_GENERATION=False`
- `ENABLE_FOLLOW_UP_GENERATION=False`
- Keep default SentenceTransformers embedding (lightweight CPU)

### Single User (Max Quality)
- `RAG_EMBEDDING_ENGINE=openai` or `ollama` with `nomic-embed-text`
- Task model: `gpt-5-nano` or `llama-3.1-8b-instant`
- `MODELS_CACHE_TTL=300`
- `ENABLE_REALTIME_CHAT_SAVE=False`

### Enterprise (High Scale)
- `DATABASE_URL=postgresql://...` (mandatory)
- `CONTENT_EXTRACTION_ENGINE=tika` (prevents memory leaks)
- `RAG_EMBEDDING_ENGINE=openai` or `ollama` (offload from process)
- `THREAD_POOL_SIZE=2000`
- `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=7`
- `ENABLE_REALTIME_CHAT_SAVE=False`
- `ENABLE_BASE_MODELS_CACHE=True`, `MODELS_CACHE_TTL=300`
- `ENABLE_QUERIES_CACHE=True`
- Vector DB: Milvus, Qdrant, or PGVector (NOT default ChromaDB)
- Redis: `timeout 1800`, `maxclients 10000`
- `RAG_SYSTEM_CONTEXT=True` for KV cache optimization

## Common Anti-Patterns

| Anti-Pattern | Impact | Fix |
|---|---|---|
| Default content extractor in production | pypdf leaks memory, containers restart | `CONTENT_EXTRACTION_ENGINE=tika` |
| SentenceTransformers at scale | ~500MB RAM per worker | `RAG_EMBEDDING_ENGINE=openai` or `ollama` |
| Redis Cluster when single suffices | Connection overload | Fix root cause: `timeout 1800`, `maxclients 10000` |
| `ENABLE_REALTIME_CHAT_SAVE=True` | Exhausts DB connections | Keep `False` (default) |
| Base64 icons in Actions/Filters | 30MB+ payload bloat per request | Host icons as static files, use `icon_url` |
| Not configuring Redis timeout | Connections accumulate forever | `timeout 1800` in redis.conf |
