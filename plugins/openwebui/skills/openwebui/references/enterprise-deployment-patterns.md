# Enterprise Deployment Patterns

## Python / Pip on Auto-Scaling VMs

Deploy `open-webui serve` as a systemd-managed process on virtual machines in a cloud auto-scaling group (AWS ASG, Azure VMSS, GCP MIG).

### When to Choose This Pattern

- Your organization has established VM-based infrastructure and operational practices
- Regulatory or compliance requirements mandate direct OS-level control
- Your team has limited container expertise but strong Linux administration skills
- You want a straightforward deployment without container orchestration overhead

### Installation

Install on each VM using pip with the `[all]` extra (includes PostgreSQL drivers):

```bash
pip install open-webui[all]
```

Create a systemd unit to manage the process:

```ini
[Unit]
Description=Open WebUI
After=network.target

[Service]
Type=simple
User=openwebui
EnvironmentFile=/etc/open-webui/env
ExecStart=/usr/local/bin/open-webui serve
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Place your environment variables in `/etc/open-webui/env`.

### Scaling Strategy

- **Horizontal scaling**: Configure your auto-scaling group to add or remove VMs based on CPU utilization or request count.
- **Health checks**: Point your load balancer health check at the `/health` endpoint (HTTP 200 when healthy).
- **One process per VM**: Keep `UVICORN_WORKERS=1` and let the auto-scaler manage capacity.
- **Sticky sessions**: Configure your load balancer for cookie-based session affinity to ensure WebSocket connections remain routed to the same instance.

### Key Considerations

| Consideration | Detail |
| :--- | :--- |
| **OS patching** | You are responsible for OS updates, security patches, and Python runtime management. |
| **Python environment** | Pin your Python version (3.11 recommended) and use a virtual environment or system-level install. |
| **Storage** | Use object storage (such as S3) or a shared filesystem (such as NFS). |
| **Tika sidecar** | Run a Tika server on each VM or as a shared service. |
| **Updates** | Scale the group to 1 instance, update the package (`pip install --upgrade open-webui`), wait for database migrations to complete, then scale back up. |

---

## Container Service

Run the official `ghcr.io/open-webui/open-webui` image on a managed container platform such as AWS ECS/Fargate, Azure Container Apps, or Google Cloud Run.

### When to Choose This Pattern

- You want container benefits (immutable images, versioned deployments, no OS management) without Kubernetes complexity
- Your organization already uses a managed container platform
- You need fast scaling with minimal operational overhead

### Image Selection

Use **versioned tags** for production stability:

```
ghcr.io/open-webui/open-webui:v0.x.x
```

Avoid the `:main` tag in production -- it tracks the latest development build and can introduce breaking changes.

### Scaling Strategy

- **Platform-native auto-scaling**: Configure your container service to scale on CPU utilization, memory, or request count.
- **Health checks**: Use the `/health` endpoint for both liveness and readiness probes.
- **Session affinity**: Enable sticky sessions on your load balancer for WebSocket stability.

### Key Considerations

| Consideration | Detail |
| :--- | :--- |
| **Storage** | Use object storage (S3, GCS, Azure Blob) or a shared filesystem (such as EFS). Container-local storage is ephemeral. |
| **Tika sidecar** | Run Tika as a sidecar container in the same task definition, or as a separate service. |
| **Secrets management** | Use your platform's secrets manager for `DATABASE_URL`, `REDIS_URL`, and `WEBUI_SECRET_KEY`. |
| **Updates** | Perform a rolling deployment with a single task first (migrations enabled), then scale remaining tasks with migrations disabled. |

### Anti-Patterns to Avoid

| Anti-Pattern | Impact | Fix |
| :--- | :--- | :--- |
| Using local SQLite | Data loss on task restart, database locks with multiple tasks | Set `DATABASE_URL` to PostgreSQL |
| Default ChromaDB | SQLite-backed vector DB crashes under multi-process access | Set `VECTOR_DB=pgvector` (or Milvus/Qdrant) |
| Inconsistent `WEBUI_SECRET_KEY` | Login loops, 401 errors, sessions that don't persist across tasks | Set the same key on every task via secrets manager |
| No Redis | WebSocket failures, config not syncing, "Model Not Found" errors | Set `REDIS_URL` and `WEBSOCKET_MANAGER=redis` |
