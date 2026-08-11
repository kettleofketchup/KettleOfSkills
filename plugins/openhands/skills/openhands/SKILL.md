---
name: openhands
last_updated: 2026-08-07
version: app 1.8 (V1), agent-server 1.26.0, agent-canvas Helm chart (OSS)
description: Self-hosted OpenHands AI coding agent. Use for Docker/Helm deploys, sandbox runtimes, LLM and LiteLLM config, subscription auth, Python SDK, MCP, skills/hooks, or multi-user auth.
---

# OpenHands

Open-source AI software development agent. A server hosts the UI and orchestration; each conversation gets an
isolated **sandbox** running an agent-server that executes the agent's commands.

## Mental Model

```
openhands server (UI + orchestration)
   │  ├─ settings/secrets in ~/.openhands  (or PVC)
   │  └─ LLM ──► provider API | LiteLLM gateway | subscription OAuth
   ▼
sandbox  (RUNTIME=docker | process | remote)
   └─ agent-server (ghcr.io/openhands/agent-server) ── terminal, file editor, browser, MCP
        └─ workspace: repo clone, .openhands/ skills + hooks
```

**V0 → V1 matters.** V1 replaced `config.toml` with environment variables and the Settings UI, and renamed
"runtime" to "sandbox" in the docs (the env var is still `RUNTIME`). Guidance mentioning `config.toml` for core
config is V0-era. → `references/env-vars.md`

## Quick Start

```bash
# uv (recommended)
uv tool install openhands --python 3.12
openhands serve

# Docker
docker run -it --rm --pull=always \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e AGENT_SERVER_IMAGE_TAG=1.26.0-python \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  -p 3000:3000 \
  --add-host host.docker.internal:host-gateway \
  --name openhands-app \
  docker.openhands.dev/openhands/openhands:1.8
```

The docker socket mount is how the server spawns sandbox containers. Mounting it grants root-equivalent host
access — never expose that instance beyond localhost without an auth proxy in front.

## Reference Index

### Deployment
- [Self-Hosting](references/self-host.md) — install paths, docker run, sandbox providers, volumes, GPU
- [Kubernetes & Helm](references/helm-k8s.md) — OSS `agent-canvas` chart, PVC layout, RBAC, ingress
- [Enterprise Chart](references/helm-enterprise.md) — Keycloak, Runtime API, sandbox namespace isolation
- [Environment Variables](references/env-vars.md) — full V1 + legacy reference by category

### LLM Configuration
- [LLM Providers](references/llm-config.md) — model strings, LiteLLM gateway, local models, custom profiles
- [Subscription Auth](references/llm-subscriptions.md) — ChatGPT/Codex OAuth login instead of API keys

### Auth & Multi-User
- [Auth & Tenancy](references/auth-tenancy.md) — Keycloak, Authentik forward-auth, per-user isolation, secrets

### Extending
- [Python SDK](references/sdk.md) — `LLM`/`Agent`/`Conversation`, tools, workspaces, agent-server API
- [MCP, Skills & Hooks](references/mcp-skills-hooks.md) — MCP servers, `.openhands/` repo customization

## Critical Rules

**OpenHands has no built-in multi-user authentication in the OSS server.** It is a single-tenant application:
anyone who reaches the port gets the agent, its secrets, and its sandbox. Multi-user means either the
enterprise deployment (Keycloak) or one instance per user behind forward-auth. → `references/auth-tenancy.md`

**The agent executes arbitrary code by design.** `RUNTIME=process` runs it directly on the host with no
isolation — acceptable for a disposable VM, never on a workstation with credentials or a shared server.

**Set a budget before pointing it at a paid key.** `MAX_BUDGET_PER_TASK` and `MAX_ITERATIONS` (default 100) are
the only things between a stuck agent loop and a large invoice.

**Pin image tags.** `--pull=always` with a floating tag silently changes agent behavior between runs. Pin both
`openhands:<ver>` and `AGENT_SERVER_IMAGE_TAG` in anything reproducible.

**The server and agent-server images are versioned separately** and must be compatible. Mismatches surface as
sandboxes that start and immediately disconnect.

## Deployment Decision

| Situation | Choice |
|-----------|--------|
| Single developer, local | `uv tool install openhands` + `RUNTIME=docker` |
| Shared server, one user | Docker + Traefik forward-auth via Authentik |
| Kubernetes, small team | OSS `agent-canvas` Helm chart, one release per user |
| Real multi-tenancy, SSO, quotas | Enterprise chart (Keycloak + Runtime API + LiteLLM); license-gated |

Per-user releases are the honest OSS path to multi-user: each gets its own PVC, secrets, and namespace, with
Authentik gating the route. It duplicates infrastructure but keeps the isolation boundary real.

## Common Failure Modes

| Symptom | Cause |
|---------|-------|
| Sandbox never starts | Docker socket not mounted, or `AGENT_SERVER_IMAGE_TAG` unpullable |
| Sandbox starts then disconnects | Server/agent-server version mismatch |
| Agent can't reach host services | Missing `--add-host host.docker.internal:host-gateway` |
| Settings lost on restart | `~/.openhands` not persisted (bind mount or PVC) |
| Runaway spend | `MAX_BUDGET_PER_TASK` / `MAX_ITERATIONS` unset |
| Writes fail on K8s PVC | `fsGroup` ≠ `10001` (agent-canvas runs as UID 10001) |
| Model not found via gateway | Missing `litellm_proxy/` prefix on `LLM_MODEL` |
