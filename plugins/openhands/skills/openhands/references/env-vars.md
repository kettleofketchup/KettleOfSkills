# OpenHands Environment Variables

V1 configures via environment variables and the Settings UI. `config.toml` is legacy (V0) for core config,
though `[mcp]` in `config.toml` is still documented for MCP servers.

## V1 Essentials

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_MODEL` | — | Model string (LiteLLM naming) |
| `LLM_API_KEY` | — | Provider key |
| `LLM_BASE_URL` | — | Custom endpoint / gateway |
| `RUNTIME` | `docker` | Sandbox provider: `docker`, `process`, `remote` |
| `OH_PERSISTENCE_DIR` | `~/.openhands` | Settings, secrets, history |
| `OH_WEB_URL` | — | External URL of the server |
| `SANDBOX_VOLUMES` | `""` | `host:container[:mode]`, comma-separated |
| `SANDBOX_CONTAINER_URL_PATTERN` | — | URL template for sandbox containers |
| `AGENT_SERVER_IMAGE_REPOSITORY` | — | e.g. `ghcr.io/openhands/agent-server` |
| `AGENT_SERVER_IMAGE_TAG` | — | e.g. `1.26.0-python` |
| `AGENT_SERVER_USE_HOST_NETWORK` | `false` | Host networking for the agent server |

## Core

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `false` | Verbose logging (also enables file logs) |
| `DISABLE_COLOR` | `false` | Plain terminal output |
| `CACHE_DIR` | `/tmp/cache` | Cache location |
| `FILE_STORE` | `memory` | Storage backend |
| `FILE_STORE_PATH` | `/tmp/file_store` | File storage dir |
| `SAVE_TRAJECTORY_PATH` | `./trajectories` | Conversation records |
| `REPLAY_TRAJECTORY_PATH` | `""` | Replay a saved trajectory |
| `FILE_UPLOADS_MAX_FILE_SIZE_MB` | `0` | `0` = unlimited |
| `FILE_UPLOADS_RESTRICT_FILE_TYPES` | `false` | Enforce extension allowlist |
| `FILE_UPLOADS_ALLOWED_EXTENSIONS` | `[".*"]` | Allowed types |
| **`MAX_BUDGET_PER_TASK`** | `0.0` | **Spend cap per task — set this** |
| **`MAX_ITERATIONS`** | `100` | **Agent step cap** |
| `DEFAULT_AGENT` | `CodeActAgent` | Agent implementation |
| `JWT_SECRET` | auto | Session token secret — pin it for stable sessions across restarts |
| `RUN_AS_OPENHANDS` | `true` | Run as the `openhands` user |
| `VOLUMES` | `""` | Mount points |

`MAX_BUDGET_PER_TASK=0.0` means unlimited. A stuck agent loop is the normal way people discover this.

## LLM

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_API_VERSION` | `""` | API version (Azure) |
| `LLM_TEMPERATURE` | `0.0` | Sampling temperature |
| `LLM_TOP_P` | `1.0` | Nucleus sampling |
| `LLM_MAX_INPUT_TOKENS` | `0` | Input cap (`0` = model default) |
| `LLM_MAX_OUTPUT_TOKENS` | `0` | Output cap |
| `LLM_MAX_MESSAGE_CHARS` | `30000` | Per-message char limit |
| `LLM_TIMEOUT` | `0` | Request timeout (s) |
| `LLM_NUM_RETRIES` | `8` | Retry attempts |
| `LLM_RETRY_MIN_WAIT` / `LLM_RETRY_MAX_WAIT` | `15` / `120` | Backoff bounds (s) |
| `LLM_RETRY_MULTIPLIER` | `2.0` | Backoff factor |
| `LLM_DROP_PARAMS` | `false` | Silently drop unsupported params |
| `LLM_CACHING_PROMPT` | `true` | Prompt caching — large cost saver, keep on |
| `LLM_DISABLE_VISION` | `false` | Disable image input |
| `LLM_CUSTOM_LLM_PROVIDER` | `""` | Provider override |
| `LLM_OLLAMA_BASE_URL` | `""` | Ollama endpoint |
| `LLM_INPUT_COST_PER_TOKEN` / `LLM_OUTPUT_COST_PER_TOKEN` | `0.0` | Pricing for local/custom models so budgets work |
| `LLM_REASONING_EFFORT` | `""` | `low`/`medium`/`high` |
| `LLM_AWS_ACCESS_KEY_ID` / `LLM_AWS_SECRET_ACCESS_KEY` / `LLM_AWS_REGION_NAME` | `""` | Bedrock |

## Agent

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGENT_LLM_CONFIG` | `""` | Named LLM config group |
| `AGENT_FUNCTION_CALLING` | `true` | Native tool calling |
| `AGENT_ENABLE_BROWSING` | `false` | Web browsing tool |
| `AGENT_ENABLE_LLM_EDITOR` | `false` | LLM-based editor |
| `AGENT_ENABLE_JUPYTER` | `false` | Notebook execution |
| `AGENT_ENABLE_HISTORY_TRUNCATION` | `true` | Truncate long histories |
| `AGENT_ENABLE_PROMPT_EXTENSIONS` | `true` | Skills/microagents |
| `AGENT_DISABLED_MICROAGENTS` | `[]` | Disable specific skills |

## Sandbox

| Variable | Default | Purpose |
|----------|---------|---------|
| `SANDBOX_TIMEOUT` | `120` | Command timeout (s) |
| `SANDBOX_USER_ID` | `1000` | UID inside the sandbox |
| `SANDBOX_BASE_CONTAINER_IMAGE` | `nikolaik/python-nodejs:python3.12-nodejs22` | Base image |
| `SANDBOX_USE_HOST_NETWORK` | `false` | Share host network (weakens isolation) |
| `SANDBOX_RUNTIME_BINDING_ADDRESS` | `0.0.0.0` | Bind address |
| `SANDBOX_ENABLE_AUTO_LINT` | `false` | Lint after edits |
| `SANDBOX_INITIALIZE_PLUGINS` | `true` | Load plugins |
| `SANDBOX_RUNTIME_EXTRA_DEPS` | `""` | Extra packages at startup |
| `SANDBOX_RUNTIME_STARTUP_ENV_VARS` | `{}` | Startup env |
| `SANDBOX_VOLUMES` | `""` | Mounts |
| `SANDBOX_KEEP_RUNTIME_ALIVE` | `false` | Keep sandbox after session |
| `SANDBOX_PAUSE_CLOSED_RUNTIMES` | `false` | Pause instead of destroy |
| `SANDBOX_CLOSE_DELAY` | `300` | Idle shutdown (s) |
| `SANDBOX_RM_ALL_CONTAINERS` | `false` | Remove containers on shutdown |
| `SANDBOX_ENABLE_GPU` | `false` | GPU passthrough |
| `SANDBOX_CUDA_VISIBLE_DEVICES` | `""` | GPU selection |
| `SANDBOX_VSCODE_PORT` | auto | VS Code server port |
| `SANDBOX_ENV_*` | — | Any such var is forwarded into the sandbox |
| `SANDBOX_API_KEY` | `""` | Remote sandbox auth |
| `SANDBOX_REMOTE_RUNTIME_API_URL` | `""` | Remote sandbox endpoint |

`SANDBOX_ENV_*` is the clean way to pass credentials into the sandbox (e.g. `SANDBOX_ENV_NPM_TOKEN`) without
exposing the server's own environment.

## Security

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECURITY_CONFIRMATION_MODE` | `false` | Require approval before each action |
| `SECURITY_SECURITY_ANALYZER` | `llm` | Analyzer implementation |
| `SECURITY_ENABLE_SECURITY_ANALYZER` | `true` | Enable risk analysis |

`SECURITY_CONFIRMATION_MODE=true` is the difference between an agent that asks before `rm -rf` and one that
doesn't. Enable it whenever the sandbox touches anything you can't recreate.

## Server

| Variable | Default |
|----------|---------|
| `FRONTEND_PORT` | `3000` |
| `BACKEND_PORT` | `8000` |
| `FRONTEND_HOST` / `BACKEND_HOST` / `WEB_HOST` | `localhost` |
| `SERVE_FRONTEND` | `true` |

## Integrations

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub auth |
| `ALLOW_INSECURE_GIT_ACCESS` | Permit plain HTTP git |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `AZURE_API_KEY` | Provider keys |
| `TAVILY_API_KEY` | Search tool |

## Debug

`DEBUG`, `DEBUG_LLM`, `DEBUG_RUNTIME`, `LOG_TO_FILE`, `LOG_ALL_EVENTS`.

`DEBUG_LLM=true` writes full prompts and responses to logs, including any secrets in context. Local only.

## Deprecated (V0)

`WORKSPACE_BASE`, `WORKSPACE_MOUNT_PATH`, `WORKSPACE_MOUNT_PATH_IN_SANDBOX`, `WORKSPACE_MOUNT_REWRITE` — all
replaced by `SANDBOX_VOLUMES`.
