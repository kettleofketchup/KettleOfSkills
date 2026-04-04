# Terminals Policies

Policies are named environment profiles that define what a terminal container looks like -- its image, resource limits, storage, environment variables, and idle timeout. They let you offer different terminal environments to different teams from a single orchestrator.

## How policies work

1. **Admin creates policies** on the orchestrator via its REST API.
2. **Admin creates terminal connections** in Open WebUI under **Settings > Connections > Open Terminal**. Each connection includes a `policy_id` field that maps it to a policy on the orchestrator.
3. **Users open a terminal** -- Open WebUI routes the request through `/p/{policy_id}/...`, and the orchestrator provisions (or reuses) a container matching that policy's spec.

Each user gets their own isolated container per policy. If a user has access to two connections with different policies, they get two independent terminals.

## Policy fields

All fields are optional. When omitted, the orchestrator falls back to its global default.

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image` | string | `TERMINALS_IMAGE` | Container image to run |
| `cpu_limit` | string | No limit | Maximum CPU (e.g., `"2"`, `"500m"`) |
| `memory_limit` | string | No limit | Maximum memory (e.g., `"4Gi"`, `"512Mi"`) |
| `storage` | string | None (ephemeral) | Persistent volume size (e.g., `"10Gi"`) |
| `storage_mode` | string | `TERMINALS_KUBERNETES_STORAGE_MODE` | How PVs are provisioned (Kubernetes only): `per-user`, `shared`, `shared-rwo` |
| `env` | object | `{}` | Key-value environment variables injected into the container |
| `idle_timeout_minutes` | integer | `TERMINALS_IDLE_TIMEOUT_MINUTES` | Minutes of inactivity before container removal |

### Storage modes (Kubernetes only)

| Mode | Behavior | PVC access mode |
| :--- | :--- | :--- |
| `per-user` | Each user gets their own PVC. Full isolation. | ReadWriteOnce |
| `shared` | Single PVC shared by all users via subPath. Requires RWX storage (e.g., NFS, EFS). | ReadWriteMany |
| `shared-rwo` | Single RWO PVC shared. All pods scheduled to same node via pod affinity. | ReadWriteOnce |

### Environment variables

The `env` field injects arbitrary key-value pairs. Common uses:

- **API keys** -- give users access to LLM APIs, cloud services, etc.
- **Egress filtering** -- set `OPEN_TERMINAL_ALLOWED_DOMAINS` to restrict outbound access. Docker backend automatically adds `NET_ADMIN` capability when set.
- **Custom configuration** -- any setting your terminal image supports

**Warning**: Environment variables are visible to the terminal user (they can run `env`). Do not store secrets here that users should not see.

## Managing policies via REST API

All endpoints require `Authorization: Bearer {TERMINALS_API_KEY}`.

### Create a policy

```bash
curl -X PUT http://localhost:3000/api/v1/policies/data-science \
  -H "Authorization: Bearer $TERMINALS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "ghcr.io/open-webui/open-terminal:latest",
    "cpu_limit": "4",
    "memory_limit": "16Gi",
    "storage": "20Gi",
    "env": {
      "OPEN_TERMINAL_ALLOWED_DOMAINS": "*.pypi.org,github.com,huggingface.co"
    },
    "idle_timeout_minutes": 60
  }'
```

### List policies

```bash
curl http://localhost:3000/api/v1/policies \
  -H "Authorization: Bearer $TERMINALS_API_KEY"
```

### Get a single policy

```bash
curl http://localhost:3000/api/v1/policies/data-science \
  -H "Authorization: Bearer $TERMINALS_API_KEY"
```

### Update a policy

Use `PUT` to upsert (creates if it doesn't exist):

```bash
curl -X PUT http://localhost:3000/api/v1/policies/data-science \
  -H "Authorization: Bearer $TERMINALS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cpu_limit": "8", "memory_limit": "32Gi"}'
```

Updating a policy does not affect running terminals. The new spec applies the next time a container is provisioned.

### Delete a policy

```bash
curl -X DELETE http://localhost:3000/api/v1/policies/data-science \
  -H "Authorization: Bearer $TERMINALS_API_KEY"
```

## Connecting policies to Open WebUI

### 1. Add a terminal connection

In the Open WebUI admin panel, go to **Settings > Connections** and add an Open Terminal connection:

| Field | Value |
| :--- | :--- |
| **URL** | The orchestrator's URL (e.g., `http://terminals-orchestrator:3000`) |
| **API Key** | The orchestrator's `TERMINALS_API_KEY` |
| **Policy ID** | The policy name you created (e.g., `data-science`) |

### 2. Restrict access with groups

Each connection supports **access grants**:

```json
[
  {
    "url": "http://orchestrator:3000",
    "key": "sk-...",
    "policy_id": "development",
    "config": {
      "access_grants": [
        { "principal_type": "group", "principal_id": "engineering", "permission": "read" }
      ]
    }
  },
  {
    "url": "http://orchestrator:3000",
    "key": "sk-...",
    "policy_id": "data-science",
    "config": {
      "access_grants": [
        { "principal_type": "group", "principal_id": "data-team", "permission": "read" }
      ]
    }
  }
]
```

## Hard caps

Global limits that clamp policy values, set as environment variables on the orchestrator:

| Environment variable | Example | Description |
| :--- | :--- | :--- |
| `TERMINALS_MAX_CPU` | `8` | Maximum CPU any policy can request |
| `TERMINALS_MAX_MEMORY` | `32Gi` | Maximum memory any policy can request |
| `TERMINALS_MAX_STORAGE` | `100Gi` | Maximum persistent storage any policy can request |
| `TERMINALS_ALLOWED_IMAGES` | `ghcr.io/open-webui/*,gcr.io/my-org/*` | Comma-separated glob patterns. Policies with non-matching images are rejected (HTTP 400). |

Hard caps are enforced at policy creation and update time. Values exceeding caps are silently clamped.

## The "default" policy

When a terminal connection has no `policy_id` (or the orchestrator receives a request without a `/p/` prefix), the global settings are used:

| Setting | Environment variable |
| :--- | :--- |
| Image | `TERMINALS_IMAGE` |
| Idle timeout | `TERMINALS_IDLE_TIMEOUT_MINUTES` |
| Storage mode | `TERMINALS_KUBERNETES_STORAGE_MODE` |

A policy named `default` in the database merges with global settings (policy values take precedence).

## API reference

All endpoints prefixed with `/api/v1` on the orchestrator.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/policies` | List all policies |
| `POST` | `/policies` | Create a new policy (returns 409 if exists) |
| `GET` | `/policies/{policy_id}` | Get a single policy |
| `PUT` | `/policies/{policy_id}` | Create or update a policy |
| `DELETE` | `/policies/{policy_id}` | Delete a policy |

### Request body (PolicyData)

```json
{
  "image": "ghcr.io/open-webui/open-terminal:latest",
  "cpu_limit": "4",
  "memory_limit": "16Gi",
  "storage": "20Gi",
  "storage_mode": "per-user",
  "env": { "KEY": "value" },
  "idle_timeout_minutes": 60
}
```

All fields optional. Omitted fields inherit from orchestrator global defaults.

## Example: multi-team setup

Create three policies via PUT: `engineering` (2 CPU, 4Gi, 10Gi storage, 120min timeout), `data-science` (8 CPU, 32Gi, 50Gi storage, egress-filtered), `intern` (1 CPU, 1Gi, no storage, 15min timeout). Then create three connections in Open WebUI with different `policy_id` values and use access grants to restrict visibility per group.
