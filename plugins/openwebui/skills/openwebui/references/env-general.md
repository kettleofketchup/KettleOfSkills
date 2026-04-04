# Open WebUI Environment Variables: General & App Configuration

Up-to-date with Open WebUI v0.8.5.

## PersistentConfig Behavior

Environment variables marked `PersistentConfig` are stored in the database after first launch. On restart, the DB value is used instead of the env var. Set `ENABLE_PERSISTENT_CONFIG=False` to force env vars (UI changes won't persist across restarts). Update PersistentConfig vars via Admin Panel or by temporarily disabling persistent config.

To fix ignored env vars: (1) set `ENABLE_PERSISTENT_CONFIG=False`, (2) update via Admin UI, (3) manually update SQLite: `docker exec -it open-webui sqlite3 /app/backend/data/webui.db "UPDATE config SET data = json_set(data, '$.ENABLE_SIGNUP', json('true'));"`, or (4) remove volume for fresh install (deletes all data).

## General

| Variable | Type | Default | Description |
|---|---|---|---|
| `WEBUI_URL` | str | `http://localhost:3000` | URL where Open WebUI is reachable. Required for OAuth/SSO. PersistentConfig. Must be set before OAuth use. |
| `ENABLE_SIGNUP` | bool | `True` | Toggles user account creation. PersistentConfig. |
| `ENABLE_SIGNUP_PASSWORD_CONFIRMATION` | bool | `False` | Adds confirm password field on signup. |
| `WEBUI_ADMIN_EMAIL` | str | `''` | Admin email for auto-creation on first startup (fresh install only). |
| `WEBUI_ADMIN_PASSWORD` | str | `''` | Admin password for auto-creation. Use with `WEBUI_ADMIN_EMAIL`. |
| `WEBUI_ADMIN_NAME` | str | `Admin` | Display name for auto-created admin. |
| `ENABLE_LOGIN_FORM` | bool | `True` | Toggles email/password sign-in elements. PersistentConfig. |
| `ENABLE_PASSWORD_AUTH` | bool | `True` | Allows password + SSO coexistence. Set `False` for SSO-only (requires `ENABLE_OAUTH_SIGNUP=True`). |
| `DEFAULT_LOCALE` | str | `en` | Default locale. PersistentConfig. |
| `DEFAULT_MODELS` | str | `''` | Default language model. PersistentConfig. |
| `DEFAULT_PINNED_MODELS` | str | `''` | Comma-separated model IDs to pin for new users. PersistentConfig. |
| `DEFAULT_MODEL_METADATA` | dict | `{}` | Global default metadata for all models. PersistentConfig. |
| `DEFAULT_MODEL_PARAMS` | dict | `{}` | Global default parameters (temperature, top_p, etc.). PersistentConfig. |
| `DEFAULT_USER_ROLE` | str | `pending` | Role for new users: `pending`, `user`, `admin`. PersistentConfig. |
| `DEFAULT_GROUP_ID` | str | `''` | Default group for new users. PersistentConfig. |
| `DEFAULT_GROUP_SHARE_PERMISSION` | str | `members` | Default share permission for new groups: `members`, `true`, `false`. |
| `ENABLE_CHANNELS` | bool | `False` | Enables channel support. PersistentConfig. |
| `ENABLE_FOLDERS` | bool | `True` | Enables chat folder organization. PersistentConfig. |
| `FOLDER_MAX_FILE_COUNT` | int | `''` (unlimited) | Max files per folder. PersistentConfig. |
| `ENABLE_NOTES` | bool | `True` | Enables notes feature. PersistentConfig. |
| `ENABLE_MEMORIES` | bool | `True` | Enables memory feature. PersistentConfig. |
| `WEBHOOK_URL` | str | - | Discord/Slack/Teams webhook. PersistentConfig. |
| `ENABLE_ADMIN_EXPORT` | bool | `True` | Admin data/DB export (SQLite only). |
| `ENABLE_ADMIN_CHAT_ACCESS` | bool | `True` | Admin access to user chats. |
| `ENABLE_ADMIN_ANALYTICS` | bool | `True` | Analytics tab visibility in admin panel. |
| `BYPASS_ADMIN_ACCESS_CONTROL` | bool | `True` | When `False`, admins see only items they have explicit permission to access. |
| `BYPASS_MODEL_ACCESS_CONTROL` | bool | `False` | When `True`, all users access all models regardless of privacy settings. |
| `ENABLE_USER_WEBHOOKS` | bool | `False` | Enables user webhooks. PersistentConfig. |
| `RESPONSE_WATERMARK` | str | `''` | Text included when copying messages. PersistentConfig. |
| `THREAD_POOL_SIZE` | int | `0` (default 40) | Thread pool for FastAPI. Set to 1000+ for large instances. |
| `SHOW_ADMIN_DETAILS` | bool | `True` | Show admin details in UI. PersistentConfig. |
| `ENABLE_PUBLIC_ACTIVE_USERS_COUNT` | bool | `True` | Active user count visibility. PersistentConfig. |
| `ENABLE_USER_STATUS` | bool | `True` | User status indicators. PersistentConfig. |
| `ENABLE_EASTER_EGGS` | bool | `True` | Easter egg features in UI. |
| `ADMIN_EMAIL` | str | - | Admin email shown by `SHOW_ADMIN_DETAILS`. PersistentConfig. |
| `ENV` | str | `dev`/`prod` | `dev` enables `/docs`. Docker defaults to `prod`. |
| `ENABLE_PERSISTENT_CONFIG` | bool | `True` | DB values override env vars when `True`. |
| `CUSTOM_NAME` | str | - | Sets `WEBUI_NAME`, polls api.openwebui.com for metadata. |
| `WEBUI_NAME` | str | `Open WebUI` | Main WebUI name. |
| `PORT` | int | `8080` | Port for Open WebUI. Use `--port` flag with `open-webui serve`. |
| `WEBUI_BUILD_HASH` | str | `dev-build` | Git SHA for releases. |
| `WEBUI_BANNERS` | list | `[]` | Banner notifications. PersistentConfig. Format: `[{"id":"","type":"info","title":"","content":"","dismissible":false,"timestamp":1000}]` |
| `USE_CUDA_DOCKER` | bool | `False` | Build with NVIDIA CUDA support. |
| `DEVICE_TYPE` | str | `cpu` | Device for model execution: `cpu`, `cuda`, `mps`. |
| `EXTERNAL_PWA_MANIFEST_URL` | str | `None` | External PWA manifest URL. |
| `LICENSE_KEY` | str | `None` | Enterprise license key. PersistentConfig. |
| `ENABLE_COMPRESSION_MIDDLEWARE` | bool | `True` | Gzip compression for HTTP responses. |
| `ENABLE_CUSTOM_MODEL_FALLBACK` | bool | `False` | Fallback to default model if base model missing. |
| `ENABLE_VERSION_UPDATE_CHECK` | bool | `True` | Automatic update checks. Disabled if OFFLINE_MODE is on. |
| `OFFLINE_MODE` | bool | `False` | Disables update checks and auto model downloads. External APIs still work. |
| `HF_HUB_OFFLINE` | int | `0` | Prevents Hugging Face connections. RAG won't work on default install if `1`. |
| `RESET_CONFIG_ON_START` | bool | `False` | Resets config.json on startup. |
| `SAFE_MODE` | bool | `False` | Disables potentially unsafe features, deactivates all functions. |
| `CORS_ALLOW_ORIGIN` | str | `*` | Allowed CORS origins (semicolon-separated). Required for WebSocket. |
| `CORS_ALLOW_CUSTOM_SCHEME` | str | `''` | Additional CORS schemes (semicolon-separated, e.g., `app;electron`). |
| `DEFAULT_PROMPT_SUGGESTIONS` | list | `[]` | Global default prompt suggestions. |

## Streaming & Chat

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_REALTIME_CHAT_SAVE` | bool | `False` | Saves every token to DB. **DO NOT enable in production.** |
| `CHAT_RESPONSE_STREAM_DELTA_CHUNK_SIZE` | int | `1` | Min tokens to batch before sending to client. Set 5-10 for high concurrency. |
| `CHAT_STREAM_RESPONSE_CHUNK_MAX_BUFFER_SIZE` | int | `None` | Max buffer size (bytes) for stream chunks. Recommended 16-20MB for image models. |
| `ENABLE_CHAT_RESPONSE_BASE64_IMAGE_URL_CONVERSION` | bool | `False` | Auto-uploads base64 images >1KB to reduce response size. |
| `ENABLE_RESPONSES_API_STATEFUL` | bool | `False` | Stateful session handling for Responses API. Experimental. |

## Directories

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATA_DIR` | str | `./data` | Base directory for data storage. |
| `FONTS_DIR` | str | - | Directory for fonts. |
| `FRONTEND_BUILD_DIR` | str | `../build` | Built frontend files location. |
| `STATIC_DIR` | str | `./static` | Static files directory. |

## Logging

| Variable | Type | Default | Description |
|---|---|---|---|
| `GLOBAL_LOG_LEVEL` | str | `INFO` | Global log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `LOG_FORMAT` | str | - | Set to `json` for structured JSON logging. |
| `ENABLE_AUDIT_STDOUT` | bool | `False` | Audit logs to stdout. |
| `ENABLE_AUDIT_LOGS_FILE` | bool | `True` | Audit logs to file. |
| `AUDIT_LOGS_FILE_PATH` | str | `${DATA_DIR}/audit.log` | Audit log file path. |
| `AUDIT_LOG_FILE_ROTATION_SIZE` | str | `10MB` | Max audit log file size before rotation. |
| `AUDIT_LOG_LEVEL` | str | `NONE` | Verbosity: `NONE`, `METADATA`, `REQUEST`, `REQUEST_RESPONSE`. |
| `MAX_BODY_LOG_SIZE` | int | `2048` | Max bytes for request/response bodies in audit logs. |
| `AUDIT_EXCLUDED_PATHS` | str | `/chats,/chat,/folders` | Paths excluded from audit logging (blacklist mode). |
| `AUDIT_INCLUDED_PATHS` | str | `''` | Paths to include (whitelist mode, overrides excluded). |

## AIOHTTP Client

| Variable | Type | Default | Description |
|---|---|---|---|
| `AIOHTTP_CLIENT_TIMEOUT` | int | `300` | General API request timeout (seconds). Empty string = no timeout. |
| `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST` | int | `10` | Timeout for fetching model lists. |
| `AIOHTTP_CLIENT_TIMEOUT_OPENAI_MODEL_LIST` | int | - | Timeout for OpenAI model list fetch. |
| `AIOHTTP_CLIENT_TIMEOUT_TOOL_SERVER` | int | inherits above | Timeout for tool server API calls. |
| `AIOHTTP_CLIENT_TIMEOUT_TOOL_SERVER_DATA` | int | `10` | Timeout for tool server metadata. |
| `AIOHTTP_CLIENT_SESSION_SSL` | bool | `True` | SSL verification for AIOHTTP sessions. |
| `AIOHTTP_CLIENT_SESSION_TOOL_SERVER_SSL` | bool | `True` | SSL verification for tool server connections. |
| `REQUESTS_VERIFY` | bool | `True` | SSL verification for synchronous requests (Tika, reranker). |
| `SSL_ASSERT_FINGERPRINT` | str | `None` | SSL assert fingerprint. PersistentConfig. |
