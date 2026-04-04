---
name: openwebui
description: Open WebUI self-hosted AI chat interface deployment, configuration, and administration. Use when deploying Open WebUI with Docker/Kubernetes/pip, configuring environment variables (OLLAMA_BASE_URL, OPENAI_API_KEY, DATABASE_URL, RAG_*, AUDIO_*, IMAGE_*), setting up SSO/OAuth/LDAP/SCIM authentication, configuring RBAC (roles, groups, permissions), managing RAG/embeddings/vector databases (ChromaDB, Milvus, PGVector, Qdrant), setting up web search providers (SearXNG, Brave, Tavily, DDGS), writing plugins (Tools, Functions, Pipes, Filters, Actions, Valves, Events), configuring MCP servers, OpenAPI tool servers, setting up image generation (AUTOMATIC1111, ComfyUI, OpenAI DALL-E, Gemini), configuring TTS/STT (Whisper, OpenAI, Edge-TTS, Kokoro), scaling with Redis/PostgreSQL, reverse proxy setup (Nginx, Caddy, HAProxy, Cloudflare Tunnel), Open Terminal setup, troubleshooting connection errors, or managing Open WebUI pipelines and extensibility.
---

# Open WebUI

Self-hosted AI chat interface supporting Ollama, OpenAI-compatible APIs, and custom pipelines. Provides RAG, web search, code execution, image generation, TTS/STT, RBAC, SSO, and extensibility via plugins/MCP.

## Quick Start
```bash
# Docker with Ollama
docker run -d -p 3000:8080 -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui ghcr.io/open-webui/open-webui:main

# pip
pip install open-webui && open-webui serve
```

## Reference Index

Load relevant reference files based on the task. Files are organized by topic area.

### Environment Variables (split by category)
- [env-configuration.md](references/env-configuration.md) -- Index pointing to split files
- [env-general.md](references/env-general.md) -- App config, directories, logging, AIOHTTP, streaming
- [env-auth.md](references/env-auth.md) -- OAuth, OIDC, SSO, security, cookies, API keys
- [env-rag.md](references/env-rag.md) -- RAG, embedding, content extraction, web search, document processing
- [env-connections.md](references/env-connections.md) -- Ollama, OpenAI, database, Redis, WebSocket, vector DBs
- [env-media.md](references/env-media.md) -- Audio STT/TTS, Whisper, image generation engines
- [env-features.md](references/env-features.md) -- Tasks, code execution, autocomplete, permissions

### Authentication & Security
- [auth-sso.md](references/auth-sso.md) -- OAuth (Google/Microsoft/GitHub/OIDC), session management, role/group mapping
- [auth-sso-trusted-header.md](references/auth-sso-trusted-header.md) -- Trusted header auth, Tailscale, Cloudflare, oauth2-proxy, Authentik, Authelia
- [auth-ldap.md](references/auth-ldap.md) -- OpenLDAP Docker setup, LDIF seeding, env vars, troubleshooting
- [auth-scim.md](references/auth-scim.md) -- SCIM 2.0 provisioning, user/group operations, filtering, Okta setup
- [rbac.md](references/rbac.md) -- Roles (admin/user/pending), groups, ACLs, headless admin
- [rbac-permissions.md](references/rbac-permissions.md) -- All permission categories (workspace, sharing, chat, features, settings)
- [rbac-api-keys.md](references/rbac-api-keys.md) -- API key setup, generation, usage examples

### Administration
- [administration.md](references/administration.md) -- Banners config, webhook types (admin/user/channel)
- [administration-analytics.md](references/administration-analytics.md) -- Dashboard, token tracking, cost estimation, API endpoints
- [administration-evaluation.md](references/administration-evaluation.md) -- Arena model, ELO leaderboard, chat snapshots

### Chat Features
- [chat-features-overview.md](references/chat-features-overview.md) -- Autocomplete, follow-up prompts, message queue
- [chat-features-params.md](references/chat-features-params.md) -- Chat parameters hierarchy, URL parameters
- [chat-features-sharing-history.md](references/chat-features-sharing-history.md) -- Chat sharing, history search
- [chat-features-multimodel-queue.md](references/chat-features-multimodel-queue.md) -- Multi-model chats, conversation organization/folders

### Code Execution
- [code-execution-overview.md](references/code-execution-overview.md) -- Backends comparison (Pyodide/Jupyter/Terminal/Terminals)
- [code-execution-python.md](references/code-execution-python.md) -- Python code interpreter, Pyodide libraries, inline images
- [code-execution-artifacts-mermaid.md](references/code-execution-artifacts-mermaid.md) -- Artifacts, MermaidJS rendering

### Reasoning & Temporal
- [reasoning-models.md](references/reasoning-models.md) -- Thinking tags, reasoning_tags config, provider compatibility
- [reasoning-models-troubleshooting.md](references/reasoning-models-troubleshooting.md) -- Ollama reasoning parser, Anthropic workarounds, FAQ

### Data Controls
- [data-controls.md](references/data-controls.md) -- Shared/archived chats, file management
- [data-controls-import-export.md](references/data-controls-import-export.md) -- JSON schema, ChatGPT migration, message tree
- [memory-connections.md](references/memory-connections.md) -- Memory tools, direct connections, CORS

### RAG & Document Processing
- [rag.md](references/rag.md) -- Chunking, markdown splitting, chunk min size
- [rag-part2.md](references/rag-part2.md) -- Embedding, re-indexing, KV cache, Google Drive, YouTube
- [document-extraction.md](references/document-extraction.md) -- Extraction overview, supported formats
- [agentic-search.md](references/agentic-search.md) -- Native vs traditional RAG, search_web/fetch_url tools, deep research

### Media Generation
- [image-generation.md](references/image-generation.md) -- Native tool-based generation, inpainting, compositing
- [speech-to-text.md](references/speech-to-text.md) -- STT config, all env vars (Whisper/OpenAI/Azure/Deepgram)
- [speech-to-text-mistral.md](references/speech-to-text-mistral.md) -- Mistral Voxtral integration
- [text-to-speech.md](references/text-to-speech.md) -- OpenAI TTS, voices, per-model voice, Azure

### Plugins & Extensibility
- [plugin-overview.md](references/plugin-overview.md) -- Architecture (Tools vs Functions vs Pipelines)
- [plugin-functions.md](references/plugin-functions.md) -- Function types overview (Pipe/Filter/Action)
- [plugin-functions-action.md](references/plugin-functions-action.md) -- Action class, multi-actions, priority
- [plugin-functions-filter.md](references/plugin-functions-filter.md) -- Filter skeleton, toggle filters, two-tier system
- [plugin-functions-filter-examples.md](references/plugin-functions-filter-examples.md) -- Stream hook, rate limiting, best practices
- [plugin-functions-pipe.md](references/plugin-functions-pipe.md) -- Pipe/manifold pattern, OpenAI proxy, internal functions
- [plugin-tools.md](references/plugin-tools.md) -- Tool taxonomy, calling modes, built-in system tools
- [plugin-tools-development.md](references/plugin-tools-development.md) -- Tool class structure, OAuth tokens, citations
- [plugin-development-events.md](references/plugin-development-events.md) -- All event types, persistence, external tool events
- [plugin-development-valves.md](references/plugin-development-valves.md) -- Valves/UserValves, password/select/dynamic inputs
- [plugin-development-rich-ui.md](references/plugin-development-rich-ui.md) -- HTMLResponse, iframe, sandbox, prompt submission
- [openapi-servers.md](references/openapi-servers.md) -- OpenAPI tool servers, mcpo proxy, CORS
- [mcp.md](references/mcp.md) -- MCP native support, auth modes, troubleshooting
- [pipelines.md](references/pipelines.md) -- Pipelines Docker setup, filter/pipe types, valves
- [plugin-migration.md](references/plugin-migration.md) -- 0.4 to 0.5 migration guide

### Workspace
- [workspace-models.md](references/workspace-models.md) -- Model creation, capabilities, global defaults
- [workspace-prompts.md](references/workspace-prompts.md) -- Slash commands, custom input types, versioning
- [workspace-knowledge.md](references/workspace-knowledge.md) -- Retrieval modes, agentic tools, API endpoints
- [workspace-skills.md](references/workspace-skills.md) -- Markdown skills, lazy-loading, import/export
- [notes.md](references/notes.md) -- Rich editor, AI enhance, agentic note tools
- [channels.md](references/channels.md) -- Real-time channels, @model tagging, setup

### Open Terminal
- [open-terminal.md](references/open-terminal.md) -- Overview, installation, connecting, file browser
- [open-terminal-advanced.md](references/open-terminal-advanced.md) -- Configuration, multi-user, security
- [terminals.md](references/terminals.md) -- Enterprise terminals, Docker/Kubernetes backends
- [terminals-policies.md](references/terminals-policies.md) -- Terminal policies configuration

### Installation & Deployment
- [install-docker.md](references/install-docker.md) -- Docker run, image variants, GPU, uninstall
- [install-docker-compose-swarm.md](references/install-docker-compose-swarm.md) -- Docker Compose, Swarm stack
- [install-docker-podman-wsl.md](references/install-docker-podman-wsl.md) -- Podman, Quadlets, WSL
- [install-python.md](references/install-python.md) -- pip, uv, venv, Conda
- [install-kubernetes.md](references/install-kubernetes.md) -- Helm chart setup
- [llm-providers.md](references/llm-providers.md) -- Ollama, OpenAI, Azure, Anthropic
- [llm-providers-compatible.md](references/llm-providers-compatible.md) -- Gemini, DeepSeek, Mistral, Groq, LiteLLM
- [llm-providers-local.md](references/llm-providers-local.md) -- vLLM, Llama.cpp, Open Responses
- [scaling.md](references/scaling.md) -- PostgreSQL, Redis, multiple instances, vector DBs
- [scaling-storage.md](references/scaling-storage.md) -- Shared storage, content extraction, observability
- [updating.md](references/updating.md) -- Update strategies, rollback, Watchtower

### Reference & Infrastructure
- [api-endpoints.md](references/api-endpoints.md) -- Chat completions, Anthropic API, RAG, filters
- [https-reverse-proxy.md](references/https-reverse-proxy.md) -- Cloudflare Tunnel, ngrok, Tailscale, Caddy, HAProxy
- [nginx-configs.md](references/nginx-configs.md) -- NPM, Let's Encrypt, self-signed, Windows
- [monitoring.md](references/monitoring.md) -- Health checks, Uptime Kuma, OpenTelemetry
- [logging.md](references/logging.md) -- Log levels, JSON format, structured logging
- [settings.md](references/settings.md) -- Admin vs User settings architecture
- [development.md](references/development.md) -- Local dev setup (SvelteKit + FastAPI)

### Troubleshooting
- [troubleshooting.md](references/troubleshooting.md) -- Connection, CORS, streaming, Ollama, password reset, RAG, SSO, audio, web search, image gen, scaling, performance, database migration

### Enterprise
- [enterprise.md](references/enterprise.md) -- Overview, licensing, integration, white-labeling
- [enterprise-security.md](references/enterprise-security.md) -- Compliance (SOC2/HIPAA/GDPR), HA architecture
- [enterprise-deployment.md](references/enterprise-deployment.md) -- Infrastructure requirements, env vars
- [enterprise-deployment-patterns.md](references/enterprise-deployment-patterns.md) -- VM/pip, container service
- [enterprise-deployment-kubernetes.md](references/enterprise-deployment-kubernetes.md) -- Helm values, HPA, updates

### Tutorials & FAQ
- [tutorials-auth.md](references/tutorials-auth.md) -- Dual OAuth, Tailscale quick start
- [tutorials-auth-tailscale.md](references/tutorials-auth-tailscale.md) -- Tailscale SSO, Docker Compose
- [tutorials-integrations.md](references/tutorials-integrations.md) -- OneDrive/SharePoint business
- [tutorials-integrations-continued.md](references/tutorials-integrations-continued.md) -- OneDrive personal, DeepSeek R1
- [faq.md](references/faq.md) -- Support, Docker networking, GPU, updating
- [faq-continued.md](references/faq-continued.md) -- STT/TTS, RAG context, API, MCP, scalability
- [sharing.md](references/sharing.md) -- Team sharing, LAN/Tailscale/Cloudflare, onboarding
