---
name: openhands
last_updated: 2026-08-12
version: app 1.8 (V1), agent-server 1.26.0 (workspace/repo + single-container architecture verified on agent-canvas built from v1.40.1), agent-canvas Helm chart (OSS)
description: Self-hosted OpenHands AI coding agent. Use for Docker/Helm deploys, sandbox runtimes, LLM and LiteLLM config, attaching repos/workspaces/backends, Python SDK, MCP, skills/hooks, or multi-user auth.
---

# OpenHands

Open-source AI software development agent. **One agent-server runs many conversations**; a UI (Agent Canvas)
connects to one or more agent-servers, which it calls *backends*.

## Mental Model

```
Agent Canvas (browser UI)  ──connects to──►  one or more BACKENDS
                                              │
                        each backend = ONE agent-server, running MANY conversations
                                              │
   ┌──────────────────────────────────────────┴───────────────────────────┐
   │ agent-server ── terminal, file editor, browser, MCP                   │
   │   ├─ settings/secrets in ~/.openhands (or PVC)                        │
   │   ├─ LLM ──► provider API | LiteLLM gateway | subscription OAuth      │
   │   └─ per conversation: its own WORKSPACE (a directory), NOT its own   │
   │      container. Conversations share the server's filesystem.          │
   └───────────────────────────────────────────────────────────────────────┘
```

**The single most common mistake: assuming a container per conversation.** That was the V0 design, and V1
deliberately removed it — upstream calls the old model "complicated, slow, and very error-prone". In V1 the
default is one long-lived agent-server; Docker is *supported but optional*. Isolation is opt-in, not inherent.

Consequences that follow, and that people get wrong:

- Conversations on one backend **share a filesystem, a process namespace and any daemon** the server can reach.
  Isolation between them is by working *directory*, nothing stronger.
- A Docker socket is **not** required to run OpenHands V1. If you mount one, it is for the agent's own tooling
  (the user's `docker compose`), not for OpenHands to spawn sandboxes.
- `DockerWorkspace` exists but is an **SDK-level** construct, scoped to a workspace and reused across
  conversations — it is not exposed in the Agent Canvas UI. → `references/sdk.md`
- **Automatic** per-run sandboxing is an **OpenHands Enterprise** feature.

### Isolation you *can* get in OSS: more backends

The UI's `Manage backends` dialog is the OSS isolation lever, and it is easy to overlook because nothing
labels it as such. Register **several agent-servers** and point work at different ones — each backend is its
own process, container or host, so they share nothing.

That makes isolation *manual and coarse* rather than automatic and per-conversation. Two things to know before
leaning on it:

- **Switching backends switches everything** — settings, LLM config, MCP servers and automations all belong to
  the backend, not the browser. A backend is a whole environment, not a lightweight context.
- Whether an *existing* conversation can be moved to a different backend is not documented; treat a
  conversation as bound to the backend it was created on until you verify otherwise.

Running one is cheap, which is what makes the pattern practical:

```bash
agent-canvas --backend-only --public      # port 8000; requires LOCAL_BACKEND_API_KEY
```

`--public` **requires** `LOCAL_BACKEND_API_KEY`, and that value is what you paste into Canvas's API Key field
(sent as `X-Session-API-Key`). There is no user auth behind it — the key *is* the security boundary, so keep
8000 firewalled and put it behind a tunnel, TLS proxy or in-cluster NetworkPolicy.
→ `references/workspaces-repos.md`

**V0 → V1 also matters for config.** V1 replaced `config.toml` with environment variables and the Settings UI,
and renamed "runtime" to "sandbox" in the docs. Guidance mentioning `config.toml` for core config, or a
`RUNTIME` env var selecting a per-conversation sandbox, is V0-era. → `references/env-vars.md`

## Which product am I looking at?

Three things share the "OpenHands" name and have different architectures. Identify yours before debugging.

| | What it is | Sandbox per conversation? |
|---|---|---|
| **`openhands` server** (`docker.openhands.dev/openhands/openhands`) | App server + UI; the Quick Start below | Historically yes (V0). Do not assume on V1 — verify against the version you run |
| **`agent-canvas`** (`ghcr.io/openhands/agent-canvas`) | All-in-one image: UI + agent-server + automation in ONE container | **No.** All conversations comingled on one pod/PVC → `references/helm-k8s.md` |
| **OpenHands Enterprise** | Licensed multi-tenant platform | Yes — this is the feature you are paying for |

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

That socket mount is the **V0-style** spawn-a-container-per-conversation path, and it is why so much older
guidance treats a Docker socket as mandatory. On V1 it is not: a plain `openhands serve` needs no socket at all.

Mount it only when you actually want container-backed execution, and know what you are granting — the Docker
API is root-equivalent on the host, so anything that can reach it can escape the container. Never expose such
an instance beyond localhost without an auth proxy in front.

## Reference Index

### Deployment
- [Self-Hosting](references/self-host.md) — install paths, docker run, sandbox providers, volumes, GPU
- [Kubernetes & Helm](references/helm-k8s.md) — OSS `agent-canvas` chart, PVC layout, RBAC, ingress
- [Enterprise Chart](references/helm-enterprise.md) — Keycloak, Runtime API, sandbox namespace isolation
- [Environment Variables](references/env-vars.md) — full V1 + legacy reference by category

### LLM Configuration
- [LLM Providers](references/llm-config.md) — model strings, LiteLLM gateway, local models, custom profiles
- [Subscription Auth](references/llm-subscriptions.md) — ChatGPT OAuth instead of API keys, plus the separate
  `CODEX_AUTH_JSON` path the codex ACP harness uses

### Auth & Multi-User
- [Auth & Tenancy](references/auth-tenancy.md) — Keycloak, Authentik forward-auth, per-user isolation, secrets

### Projects
- [Workspaces, Repos & Backends](references/workspaces-repos.md) — attaching a repo, the workspaces API, why
  there is no git-provider UI when self-hosted

### Extending
- [Python SDK](references/sdk.md) — `LLM`/`Agent`/`Conversation`, tools, workspaces, agent-server API
- [MCP, Skills & Hooks](references/mcp-skills-hooks.md) — MCP servers, `.openhands/` repo customization

## Critical Rules

**OpenHands has no built-in multi-user authentication in the OSS server.** It is a single-tenant application:
anyone who reaches the port gets the agent, its secrets, and its sandbox. Multi-user means either the
enterprise deployment (Keycloak) or one instance per user behind forward-auth. → `references/auth-tenancy.md`

**The agent executes arbitrary code by design, and on V1 the default is unsandboxed.** Running in-process on
the host is acceptable for a disposable VM, never on a workstation with credentials or a shared server. On
agent-canvas this is not a setting you can change — the agent runs in the pod, so the pod's whole trust
boundary (mounted secrets, service-account token, reachable services) is what the agent gets.

**Set a budget before pointing it at a paid key.** `MAX_BUDGET_PER_TASK` and `MAX_ITERATIONS` (default 100) are
the only things between a stuck agent loop and a large invoice.

**Pin image tags.** `--pull=always` with a floating tag silently changes agent behavior between runs. Pin both
`openhands:<ver>` and `AGENT_SERVER_IMAGE_TAG` in anything reproducible.

**The server and agent-server images are versioned separately** and must be compatible. Mismatches surface as
sandboxes that start and immediately disconnect.

**Git provider integration is a Cloud/enterprise feature — it does not exist in a self-hosted agent-server.**
There is no "add a repository" UI and no provider endpoints. You clone onto the agent-server and register the
directory as a *workspace*. A "backend" is another agent-server, never a repo.
→ `references/workspaces-repos.md`

## Deployment Decision

| Situation | Choice |
|-----------|--------|
| Single developer, local | `uv tool install openhands` + `openhands serve` |
| Shared server, one user | Docker + Traefik forward-auth via Authentik |
| Kubernetes, small team | OSS `agent-canvas` Helm chart, one release per user |
| **Work must not see other work** | Multiple backends (one agent-server per workspace/VM/pod), registered in `Manage backends` |
| Automatic per-run sandboxing, SSO, quotas | Enterprise chart (Keycloak + Runtime API + LiteLLM); license-gated |

Isolation in OSS is achieved by **running more agent-servers**, not by configuring one. Conversations on a
single backend always share everything; separate backends share nothing. The cost is that each backend carries
its own settings, LLM config and MCP servers, so they are environments to provision, not contexts to toggle.

Per-user releases are the honest OSS path to multi-user: each gets its own PVC, secrets, and namespace, with
Authentik gating the route. It duplicates infrastructure but keeps the isolation boundary real.

## Common Failure Modes

| Symptom | Cause |
|---------|-------|
| Sandbox never starts | Docker socket not mounted, or `AGENT_SERVER_IMAGE_TAG` unpullable |
| Sandbox starts then disconnects | Server/agent-server version mismatch |
| Looking for the per-conversation container and not finding one | On V1/agent-canvas there isn't one — conversations share the server. Not a fault |
| Agent shell says `docker.sock` missing | Expected on agent-canvas. The image ships no daemon; adding one is a deployment change, not a setting |
| One conversation clobbers another's files/containers/ports | Working as designed within a backend. The OSS fix is a second backend, not a setting |
| Added a backend, but its LLM/MCP/settings are empty | Correct — that config lives on the backend. Each one is configured separately |
| Agent can't reach host services | Missing `--add-host host.docker.internal:host-gateway` |
| Settings lost on restart | `~/.openhands` not persisted (bind mount or PVC) |
| Runaway spend | `MAX_BUDGET_PER_TASK` / `MAX_ITERATIONS` unset |
| Writes fail on K8s PVC | `fsGroup` ≠ `10001` (agent-canvas runs as UID 10001) |
| Model not found via gateway | Missing `litellm_proxy/` prefix on `LLM_MODEL` |
| No way to add a repo in the UI | Working as designed — clone onto the agent-server, then `+ Add Workspace` |
| "ChatGPT authentication is invalid" from an ACP agent | `CODEX_AUTH_JSON` failed an offline *shape* check — usually a wrapped paste, or an api-key auth.json. Not expiry |
| Codex ignores `~/.codex/auth.json` | By design; the ACP harness reads the `CODEX_AUTH_JSON` secret into a temp `CODEX_HOME` |
| Workspace list empties on restart | `workspaces.json` under `$OH_PERSISTENCE_DIR` not on a persisted volume |
