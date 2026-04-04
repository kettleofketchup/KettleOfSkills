# Open WebUI Troubleshooting

## Connection Errors

### HTTPS/TLS/CORS/WebSocket Issues

**Symptoms:** Empty `"{}"` responses, `"Unexpected token 'd'"` errors, garbled markdown during streaming, WebSocket failures, login/session issues, CORS errors.

**Required env vars for HTTPS + reverse proxy:**
```bash
WEBUI_URL=https://your-domain.com          # Set BEFORE first OAuth use
CORS_ALLOW_ORIGIN="https://domain;http://domain;https://ip;http://localhost:3000"
WEBUI_SESSION_COOKIE_SECURE=true
WEBUI_AUTH_COOKIE_SECURE=true
WEBUI_SESSION_COOKIE_SAME_SITE=lax         # Use lax for OAuth
WEBUI_AUTH_COOKIE_SAME_SITE=lax
```

### Garbled Markdown / Streaming Corruption

**Cause:** Nginx proxy buffering re-chunks SSE streams, breaking markdown tokens.

**Fix:** Add to nginx location block:
```nginx
proxy_buffering off;
proxy_cache off;
```

For HAProxy: avoid `option http-buffer-request` for SSE. For Caddy: handles SSE correctly by default.

### Frontend vs Backend Connections

| Request Origin | What `localhost` Means |
|---|---|
| Browser (client-side) | Machine running the browser |
| Backend (server-side) | Machine/container running Open WebUI |

For Docker backend connections, use: Docker service names, `host.docker.internal`, or internal IPs.

### Ollama Connection

- Set `OLLAMA_HOST=0.0.0.0` on Ollama to listen on all interfaces
- Docker: use `--network=host` or `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- Podman on macOS: use `http://host.containers.internal:11434`

### Slow Model List Loading

**Cause:** Unreachable endpoints in connections config. Default 10s timeout per endpoint.

**Fixes:** `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=3`, remove unreachable endpoints in Admin > Connections, or recover with `RESET_CONFIG_ON_START=true`.

### SSL Issues

- Hugging Face SSL: set `HF_ENDPOINT=https://hf-mirror.com/`
- Self-signed certs (Tika/Ollama): `REQUESTS_VERIFY=false` (sync), `AIOHTTP_CLIENT_SESSION_SSL=false` (async)
- Web search SSL: `ENABLE_WEB_LOADER_SSL_VERIFICATION=false`
- Proxy SSL errors: fix `HTTPS_PROXY` to use HTTPS, or set `NO_PROXY=api.service.com`

### Slow Performance on Low-Spec Hardware

Set `DATABASE_ENABLE_SESSION_SHARING=false`.

## Password Reset

### Docker
```bash
htpasswd -bnBC 10 "" your-new-password | tr -d ':\n'
docker run --rm -it -v open-webui:/data alpine
# Inside: apk add apache2-utils sqlite && sqlite3 /data/webui.db
# SQL: UPDATE auth SET password='HASH' WHERE email='admin@example.com';
```

### Local Install
```bash
sqlite3 backend/data/webui.db "UPDATE auth SET password='HASH' WHERE email='admin@example.com';"
```

### Complete Reset
Delete `webui.db` (removes ALL data including accounts and chat history).

## RAG Troubleshooting

| Problem | Fix |
|---|---|
| Model can't "see" content | Check content extractor (use Tika/Docling) |
| Only partial content used | Enable Full Context Mode or Bypass Embedding |
| 2048 token limit | Increase model context (8192+ for web, 16384+ ideal) |
| Bad retrieval accuracy | Switch to better embedding model, reindex |
| `NoneType encode` error | Re-save embedding model in Admin > Documents |
| Slow follow-up responses | `RAG_SYSTEM_CONTEXT=True` (KV cache fix) |
| API "empty content" error | Wait for file processing status=completed before adding to KB |
| CUDA OOM during embedding | Reduce batch size, isolate GPU, or restart container |
| PDF images not extracted | Use Tika/Docling, enable PDF Extract Images OCR |
| Worker dies during upload | Switch from default ChromaDB (SQLite not fork-safe) |
| KB not working with model | Check global Function Calling setting, enable Builtin Tools |
| 429 rate limit on embedding | Set `RAG_EMBEDDING_CONCURRENT_REQUESTS=5` |

### Knowledge Base Not Working with Model

Open WebUI has two RAG modes: Default (auto-injects context) and Native Function Calling (model must actively call tools). If global `Function Calling: native` is set in Admin > Settings > Models, all models inherit it. Per-model settings override globals. For native mode, enable Builtin Tools and add system prompt hints. Or disable Native Function Calling for classic auto-injection behavior.

## SSO & OAuth Troubleshooting

**Common mistakes:** Using wrong env var names (use `OAUTH_CLIENT_ID` not `OPENID_CLIENT_ID`).

**Required OIDC vars:** `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`, `OPENID_PROVIDER_URL`, `ENABLE_OAUTH_SIGNUP=true`.

**Callback URLs:** OIDC: `/oauth/oidc/callback`, Microsoft: `/oauth/microsoft/callback`, Google: `/oauth/google/callback`.

**Persistent config conflicts:** `ENABLE_OAUTH_PERSISTENT_CONFIG` defaults to `false` (env vars take priority). Set explicitly if DB values override env vars.

**Cookie issues:** Use `WEBUI_SESSION_COOKIE_SAME_SITE=lax`, set `WEBUI_SECRET_KEY` consistently.

**CSRF errors:** Verify `WEBUI_URL` matches exactly, set `WEBUI_SECRET_KEY` and `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY`.

**Multi-instance:** Same `WEBUI_SECRET_KEY` + `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY` on all replicas, configure Redis.

**Nginx caching:** Exclude `/api`, `/oauth`, `/callback`, `/login`, `/ws` from server-side caching.

**Kubernetes YAML:** Watch for trailing spaces in env var names inside quotes.

**Provider-specific:**
- Microsoft: Use `MICROSOFT_CLIENT_ID`/`SECRET`/`TENANT_ID`, not generic OIDC vars. Set `OPENID_PROVIDER_URL=https://login.microsoftonline.com/TENANT_ID/v2.0/.well-known/openid-configuration`.
- Authentik: `OPENID_PROVIDER_URL=https://authentik-domain/application/o/app-slug/.well-known/openid-configuration`
- Google: `OPENID_PROVIDER_URL=https://accounts.google.com/.well-known/openid-configuration`

**Debug:** Set `GLOBAL_LOG_LEVEL=DEBUG`, check browser cookies for `oauth_session_id`, test without reverse proxy.

## Audio Troubleshooting

**Microphone needs HTTPS** (or localhost). Chromium flag: `chrome://flags/#unsafely-treat-insecure-origin-as-secure`. Firefox: `about:config` > `dom.securecontext.allowlist`.

**TTS loading forever:** If using local Transformers TTS, fix datasets library: `EXTRA_PIP_PACKAGES=datasets==3.6.0`. Or switch to external TTS (OpenAI Edge TTS).

**Whisper compute type error:** Set `WHISPER_COMPUTE_TYPE=float16` for GPU. Use `:main` image instead of `:cuda` for old GPUs.

**Docker networking for TTS:** Use container name (`http://openai-edge-tts:5050/v1`) not `localhost`.

**Quick audio setup (free):** STT: leave engine empty (local Whisper). TTS: OpenAI Edge TTS container (`travisvn/openai-edge-tts:latest`) on port 5050.

## Web Search Troubleshooting

- **Fails behind proxy:** Enable `WEB_SEARCH_TRUST_ENV=True` in Admin > Web Search
- **SearXNG 403:** Add `json` to SearXNG `settings.yml` formats list
- **Empty results:** Increase model context to 16384+, adjust `WEB_SEARCH_RESULT_COUNT`
- **Timeouts:** Set `WEB_SEARCH_CONCURRENT_REQUESTS=1` (Brave free tier)

## Image Generation Troubleshooting

- **Not generating:** Verify Image Generation enabled in Admin > Images, check API key/URL
- **Azure OpenAI error:** Use API version `2025-04-01-preview` or later
- **ComfyUI JSON errors:** Must use "Save (API Format)" from ComfyUI dev mode
- **A1111 connection refused:** Run with `--api` flag
- **Docker connectivity:** Use `http://host.docker.internal:7860`

## Scaling & Multi-Replica

**Core requirements:** Same `WEBUI_SECRET_KEY` on all replicas, PostgreSQL (not SQLite), Redis for WebSockets, shared storage (RWX PVC), external vector DB (not default ChromaDB).

**Login loops/401:** Different secret keys across replicas. Fix: set same `WEBUI_SECRET_KEY`.

**WebSocket 403:** Configure `CORS_ALLOW_ORIGIN` with all access URLs, enable Redis for WebSockets.

**Config mismatch:** Set `REDIS_URL` for Pub/Sub config sync across replicas.

**DB locked errors:** Migrate from SQLite to PostgreSQL.

**Worker crashes during upload:** Switch from default ChromaDB to pgvector/milvus/qdrant or ChromaDB HTTP mode.

**Safe update procedure:** Either designate one migration pod (`ENABLE_DB_MIGRATIONS=True` on master only) or scale to 1 replica during upgrades.

**Pool sizing:** `Total connections = (POOL_SIZE + MAX_OVERFLOW) x replicas x UVICORN_WORKERS`. Keep under DB `max_connections`.

**Function/tool pip crashes:** Set `ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS=False`, pre-install packages in Dockerfile.

## Performance & Optimization

**Task models:** Use fast, cheap non-reasoning models (gpt-5-nano, gemma3:1b) for title/tag/query generation.

**Model caching:** `ENABLE_BASE_MODELS_CACHE=True` + `MODELS_CACHE_TTL=300` for production.

**KV cache:** `RAG_SYSTEM_CONTEXT=True` for fast follow-up responses.

**Database:** PostgreSQL mandatory for scale. `ENABLE_REALTIME_CHAT_SAVE=False` always. `DATABASE_ENABLE_SESSION_SHARING=True` for PostgreSQL with resources.

**Content extraction:** Default pypdf leaks memory. Use `CONTENT_EXTRACTION_ENGINE=tika` in production.

**Embeddings:** Default SentenceTransformers uses ~500MB/worker. Use `RAG_EMBEDDING_ENGINE=openai` or `ollama` at scale.

**High concurrency:** `THREAD_POOL_SIZE=2000`, `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE=7`, `AIOHTTP_CLIENT_TIMEOUT=1800`.

**Cloud latency:** Co-locate DB with app (aim for <2ms latency). Use SSD block storage, not NFS/SMB for SQLite.

## Database Migration (Manual)

Only needed if automatic migration fails. Always backup first.

```bash
docker stop open-webui
docker run --rm -it -v open-webui:/app/backend/data --entrypoint /bin/bash ghcr.io/open-webui/open-webui:main
cd /app/backend/open_webui
export DATABASE_URL="sqlite:////app/backend/data/webui.db"
export WEBUI_SECRET_KEY=$(cat /app/backend/.webui_secret_key)
alembic current -v    # Check current state
alembic heads          # Check target
alembic upgrade head   # Apply migrations
```

**"Table already exists":** Previous migration partially completed. Options: restore backup, drop table + re-run, or `alembic stamp <revision>` (skips data backfill).

**"No such table":** Migrations didn't apply. Run `alembic upgrade head`.

**Multiple failures after version jump:** Step through one migration at a time. Stamp past "already exists" errors, investigate other errors.
