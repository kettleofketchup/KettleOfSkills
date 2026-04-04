# Terminals (Enterprise)

**Terminals** is an enterprise orchestration layer for Open Terminal that provisions a fully isolated terminal container for every user. Instead of sharing a single container, each person gets their own -- with separate files, processes, resource limits, and network isolation.

## Why Terminals?

Open Terminal's built-in multi-user mode works for small, trusted teams but everyone shares the same container, CPU, memory, and network. Terminals solves this:

| | Built-in multi-user | Terminals |
| :--- | :--- | :--- |
| **Isolation** | Separate files, shared system | Fully separate containers |
| **Resources** | Shared CPU, memory, network | Per-user CPU, memory, and storage limits |
| **Provisioning** | Always running | On-demand. Created on first use, cleaned up when idle |
| **Environments** | One setup for everyone | Multiple policies for different teams |
| **Infrastructure** | Single container | Docker host or Kubernetes cluster |
| **Best for** | Small trusted teams | Production, larger teams, untrusted users |

## How it works

1. A user activates a terminal in Open WebUI.
2. Open WebUI proxies the request to the **Terminals orchestrator**.
3. The orchestrator provisions a personal Open Terminal container for that user (or reconnects to an existing one).
4. All traffic is proxied through the orchestrator. The user never connects to their container directly.
5. Idle containers are automatically cleaned up after a configurable timeout. Data optionally persists across sessions.

## Authentication

| Mode | When to use |
| :--- | :--- |
| **Open WebUI JWT** | Production. Set `TERMINALS_OPEN_WEBUI_URL` and the orchestrator validates tokens against your Open WebUI instance. |
| **Shared API key** | Standard. Set `TERMINALS_API_KEY` to a shared secret that Open WebUI includes in requests. |
| **Open** | Development only. No auth -- do not use in production. |

## Docker Backend

Runs on a single Docker host. The orchestrator uses the Docker API to create and manage containers.

### Quick start with Docker Compose

Deploy Open WebUI + Terminals orchestrator together. The `terminals` service needs `TERMINALS_BACKEND=docker`, `TERMINALS_API_KEY`, `TERMINALS_IMAGE`, `TERMINALS_NETWORK`, and `TERMINALS_IDLE_TIMEOUT_MINUTES`. Mount Docker socket (`/var/run/docker.sock`) and a data volume. Open WebUI connects via `TERMINAL_SERVER_CONNECTIONS` env var pointing at `http://terminals:3000`.

**Warning**: The orchestrator mounts the Docker socket. In production, consider using a Docker socket proxy to restrict allowed API calls.

Set the shared API key in `.env`: `TERMINALS_API_KEY=change-me-to-a-strong-random-value`

### Docker Backend Configuration

#### Core settings

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TERMINALS_BACKEND` | `docker` | Backend type |
| `TERMINALS_API_KEY` | (empty) | Shared secret for authenticating requests. Required. |
| `TERMINALS_IMAGE` | `ghcr.io/open-webui/open-terminal:latest` | Default container image for user instances |
| `TERMINALS_PORT` | `3000` | Port the orchestrator listens on |
| `TERMINALS_HOST` | `0.0.0.0` | Address the orchestrator binds to |

#### Docker-specific settings

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TERMINALS_NETWORK` | (empty) | Docker network for user containers |
| `TERMINALS_DOCKER_HOST` | `127.0.0.1` | Address for published container ports (only when `TERMINALS_NETWORK` not set) |
| `TERMINALS_DATA_DIR` | `data/terminals` | Host directory for per-user workspace data |

#### Lifecycle

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TERMINALS_IDLE_TIMEOUT_MINUTES` | `0` (disabled) | Minutes of inactivity before container removal. Set to `30` for typical usage. |

#### Resource limits

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TERMINALS_MAX_CPU` | (empty) | Hard cap on CPU for user containers (e.g., `2`) |
| `TERMINALS_MAX_MEMORY` | (empty) | Hard cap on memory (e.g., `4Gi`) |

### Container lifecycle details

- **Naming**: Containers named `terminals-{policy_id}-{user_id}`
- **Health checks**: Orchestrator polls `/health` endpoint up to 15 seconds
- **Reconciliation**: On restart, rediscovers existing containers by label
- **Conflict handling**: Force-removes stale containers, retries up to 3 times

### Limitations

- Single host -- all containers run on one Docker host
- No built-in HA -- if orchestrator goes down, sessions are interrupted (containers keep running and reconcile on restart)
- Docker socket required

## Kubernetes Operator

Production-grade deployment using a Kopf-based operator. Watches `Terminal` custom resources and manages per-user Pods, Services, PVCs, and Secrets.

### Architecture

| Component | Role |
| :--- | :--- |
| **Orchestrator** | FastAPI service that receives requests, creates Terminal CRs, and proxies traffic to user Pods |
| **Operator** | Kopf controller that watches Terminal CRs and reconciles infrastructure |
| **Terminal CRD** | `terminals.openwebui.com/v1alpha1` custom resource representing a user's terminal |

### Deployment with Helm

Enable via the Open WebUI Helm chart subchart: set `terminals.enabled: true` in your values file. Key values: `terminals.apiKey` (auto-generated if empty), `terminals.crd.install: true`, operator image `ghcr.io/open-webui/terminals-operator`, orchestrator image `ghcr.io/open-webui/terminals` with `backend: kubernetes-operator`, `terminalImage`, and `idleTimeoutMinutes: 30`.

```bash
helm upgrade --install open-webui open-webui/open-webui -f values.yaml --namespace open-webui --create-namespace
```

When `terminals.enabled` is `true`, the chart automatically sets `TERMINAL_SERVER_CONNECTIONS`.

### Terminal CRD spec fields

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `userId` | string | (required) | Open WebUI user ID |
| `image` | string | `ghcr.io/open-webui/open-terminal:latest` | Container image |
| `resources.requests.cpu` | string | `100m` | CPU request |
| `resources.requests.memory` | string | `256Mi` | Memory request |
| `resources.limits.cpu` | string | `1` | CPU limit |
| `resources.limits.memory` | string | `1Gi` | Memory limit |
| `idleTimeoutMinutes` | integer | `30` | Inactivity timeout |
| `packages` | array | `[]` | Apt packages to pre-install |
| `pipPackages` | array | `[]` | Pip packages to pre-install |
| `persistence.enabled` | boolean | `true` | Enable persistent storage via PVC |
| `persistence.size` | string | `1Gi` | PVC size |
| `persistence.storageClass` | string | (cluster default) | Storage class |

### Terminal CRD status fields

| Field | Description |
| :--- | :--- |
| `phase` | `Pending`, `Provisioning`, `Running`, `Idle`, `Error` |
| `podName` | Name of the terminal Pod |
| `serviceName` | Name of the terminal Service |
| `serviceUrl` | Full in-cluster URL |
| `apiKeySecret` | Secret holding the terminal's API key |
| `lastActivityAt` | ISO 8601 timestamp of last proxied request |

### Idle cleanup lifecycle

1. Operator checks activity every 60 seconds
2. If idle longer than `idleTimeoutMinutes`, deletes the Pod (not the CR, PVC, or Secret)
3. Status set to `phase: Idle`
4. On next request, new Pod provisioned with same PVC reattached
5. User data persists across idle cycles

### RBAC requirements

Operator ServiceAccount needs: get/list/watch/create/update/patch/delete on `terminals.openwebui.com`, pods, services, PVCs, secrets; create on events; get/list/watch/create/update/patch on configmaps and leases (Kopf leader election).

### Monitoring

```bash
kubectl get terminals -n open-webui
kubectl describe terminal <name> -n open-webui
kubectl get terminals -n open-webui -w
kubectl logs -n open-webui deployment/<release>-terminals-operator --tail=50
kubectl logs -n open-webui deployment/<release>-terminals-orchestrator --tail=50
```

Terminals requires an Open WebUI Enterprise License.
