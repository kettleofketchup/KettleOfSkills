---
name: litellm
last_updated: 2026-04-05
version: v1.82.3-stable (latest stable), v1.83.1-nightly (latest nightly)
description: "LiteLLM AI gateway proxy for unified LLM API access. Use when deploying LiteLLM proxy with Docker/Helm/Kubernetes, writing config.yaml (model_list, router_settings, litellm_settings, general_settings), managing virtual API keys and spend tracking, configuring JWT/OIDC token auth, setting up SSO with Generic OIDC (Authentik, Keycloak, Auth0), configuring RBAC (organizations, teams, users, roles), integrating with Langfuse observability, connecting Open WebUI as a frontend, adding vLLM as a provider backend, configuring Redis caching, setting up fallbacks and load balancing, health checks, or logging to 20+ backends."
---

# LiteLLM Proxy

OpenAI-compatible API gateway routing to 100+ LLM providers with unified auth, spend tracking, rate limiting, and observability.

## Quick Start

```bash
# Docker (stable)
docker run -v $(pwd)/config.yaml:/app/config.yaml \
  -e LITELLM_MASTER_KEY=sk-1234 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/litellm \
  -p 4000:4000 \
  docker.litellm.ai/berriai/litellm:main-stable \
  --config /app/config.yaml

# Helm
helm install litellm oci://docker.litellm.ai/berriai/litellm-helm
```

## Docker Image Tags

| Tag | Use |
|-----|-----|
| `main-stable` | Production (recommended) |
| `main-latest` | Bleeding edge nightly |
| `main-v1.82.3` | Pinned version |
| `litellm-non_root:main-stable` | Non-root container |

Registries: `docker.litellm.ai/berriai/litellm`, `ghcr.io/berriai/litellm-database`

## Config Structure (config.yaml)

Five top-level sections:

```yaml
model_list:          # Model deployments (provider, api_base, api_key)
router_settings:     # Load balancing, retries, Redis, routing strategy
litellm_settings:    # Callbacks, caching, fallbacks, timeouts
general_settings:    # master_key, database_url, JWT auth, health checks
environment_variables:  # Runtime env vars
```

## Reference Index

### Auth & Access Control
- [Virtual Keys & Spend Tracking](references/auth-virtual-keys.md) - Key CRUD, budgets, rate limits, spend tracking
- [JWT/OIDC & SSO](references/auth-jwt-sso.md) - JWT token auth, Generic OIDC, SSO providers, claim mapping
- [RBAC & User Management](references/rbac-user-management.md) - Orgs, teams, users, roles hierarchy

### Proxy Operations
- [Proxy Config & Deployment](references/proxy-config.md) - config.yaml deep dive, Docker Compose, Helm, Redis HA, workers
- [Reliability & Caching](references/reliability-caching.md) - Fallbacks, retries, routing strategies, cache backends
- [Logging & Health](references/logging-health.md) - 20+ logging backends, health endpoints, privacy controls

### Integrations
- [Langfuse](references/integrations/langfuse.md) - Observability with traces, sessions, metadata, redaction
- [Open WebUI](references/integrations/openwebui.md) - LiteLLM as OpenAI-compatible backend for Open WebUI
- [vLLM](references/integrations/vllm.md) - Self-hosted vLLM model serving via `hosted_vllm/` provider
- [Authentik](references/integrations/authentik.md) - SSO and JWT auth via Authentik Generic OIDC

## Key Environment Variables

| Variable | Purpose |
|----------|---------|
| `LITELLM_MASTER_KEY` | Admin key (must start with `sk-`) |
| `LITELLM_SALT_KEY` | Encryption key for stored credentials (immutable after setup) |
| `DATABASE_URL` | PostgreSQL connection string (required for key management) |
| `JWT_PUBLIC_KEY_URL` | OIDC JWKS endpoint (comma-separated for multiple) |
| `PROXY_BASE_URL` | Public URL of proxy (required for SSO callback) |

## Health Endpoints

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `/health` | Yes | Full model health (makes real API calls) |
| `/health/readiness` | No | DB connectivity check |
| `/health/liveliness` | No | Alive check |
| `/health/services` | Yes | Integration health (langfuse, datadog) |

## Production Notes

- Minimum 4 CPU cores, 8 GB RAM
- Use `--num_workers 8` for scaling, `--max_requests_before_restart 10000` for memory recycling
- Redis required for >1000 RPS or shared rate limits across replicas
- Remove `--detailed_debug` in production
- K8s probes: liveness=`/health/liveliness`, readiness=`/health/readiness`, `initialDelaySeconds: 120`
