# OpenHands Enterprise (Self-Hosted Cloud) Chart

License-gated multi-tenant platform. The OSS single-tenant chart is in `helm-k8s.md`.

## Access

Distributed through Replicated; available to select customers on request.

```bash
helm registry login registry.replicated.com \
  --username <license-email> --password <license-id>

kubectl create namespace openhands
kubectl create namespace openhands-runtimes

helm install openhands oci://registry.replicated.com/openhands/openhands \
  --namespace openhands --values values.yaml
```

### Components

| Component | Role |
|-----------|------|
| OpenHands Server | UI and orchestration |
| Runtime API | Sandbox lifecycle: provision, scale, clean up |
| Keycloak | Identity and access management |
| LiteLLM proxy | Model routing and per-user keys |
| PostgreSQL | Persistence |
| Redis | Cache/queue |
| MinIO / S3 | Conversation history |

### Required Secrets (namespace `openhands`)

`jwt-secret`, `keycloak-admin`, `keycloak-realm`, `postgres-password`, `redis`, `lite-llm-api-key`,
`admin-password`, `default-api-key`, `sandbox-api-key`, `litellm-env-secrets` (holds `ANTHROPIC_API_KEY`),
`github-app`.

### values.yaml Skeleton

```yaml
ingress:
  enabled: true
  host: app.openhands.example.com
  class: traefik
tls:
  enabled: false          # true when the chart terminates TLS itself

github:
  enabled: true

postgresql:
  auth: { database: openhands }
databaseMigrations:
  createDatabases: true

keycloak:
  enabled: true
  ingress:
    enabled: true
    hostname: auth.openhands.example.com

sandbox:
  apiHostname: https://runtime-api.openhands.example.com

env:
  RUNTIME_URL_PATTERN: "https://{runtime_id}-runtime.openhands.example.com"
  LITELLM_DEFAULT_MODEL: litellm_proxy/claude-sonnet-4-5

runtime-api:
  sandbox_namespace: openhands-runtimes
  ingress:
    enabled: true
    host: runtime-api.openhands.example.com
  databaseMigrations:
    createDatabases: true
  env:
    RUNTIME_BASE_URL: runtime.openhands.example.com
    RUNTIME_URL_SEPARATOR: "-"
    RUNTIME_DISABLE_SSL: "false"
    STORAGE_CLASS: <storage-class>

filestore:
  ephemeral: true
minio:
  persistence: { enabled: true }

litellm-helm:
  enabled: true
  proxy_config:
    model_list:
      - model_name: claude-sonnet-4-5
        litellm_params:
          model: anthropic/claude-sonnet-4-5
          api_key: os.environ/ANTHROPIC_API_KEY
```

Each sandbox gets its own hostname via `RUNTIME_URL_PATTERN`, so **wildcard DNS and a wildcard certificate**
covering `*.runtime.openhands.example.com` are mandatory. cert-manager DNS-01 required.

The embedded PostgreSQL is proof-of-concept only — point at CloudNativePG or a managed instance for anything
real.

### Preflight

```bash
preflight secret/openhands/openhands-preflight
kubectl get pods -n openhands --watch
```

## Sandbox Isolation on Kubernetes

Agent sandboxes run in `openhands-runtimes`. Harden that namespace, not the app namespace:

- ResourceQuota + LimitRange — an agent loop can otherwise fill the cluster
- NetworkPolicy denying egress except the LLM gateway and package registries
- No service account token automounting
- gVisor or Sysbox runtime class for kernel-level isolation (the enterprise docs cover Sysbox)

Sandboxes execute model-generated code. The namespace boundary is the security boundary — treat it the way you
would a CI runner pool that builds untrusted pull requests.
