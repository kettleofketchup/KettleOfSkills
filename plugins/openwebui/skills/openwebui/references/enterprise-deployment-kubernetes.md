# Kubernetes with Helm

Deploy using the official Open WebUI Helm chart on any Kubernetes distribution (EKS, AKS, GKE, OpenShift, Rancher, self-managed).

**Prerequisites:** Configure shared infrastructure requirements first -- PostgreSQL, Redis, a vector database, shared storage, and content extraction.

## When to Choose This Pattern

- Your organization runs Kubernetes and has platform engineering expertise
- You need declarative infrastructure-as-code with GitOps workflows
- You require advanced scaling (HPA), rolling updates, and pod disruption budgets
- You are deploying for hundreds to thousands of users in a mission-critical environment

## Helm Chart Setup

```bash
# Add the repository
helm repo add open-webui https://open-webui.github.io/helm-charts
helm repo update

# Install with custom values
helm install openwebui open-webui/open-webui -f values.yaml
```

Example `values.yaml` overrides:

```yaml
replicaCount: 3

# Database: use an external PostgreSQL instance
databaseUrl: "postgresql://user:password@db-host:5432/openwebui"

# WebSocket & Redis
websocket:
  enabled: true
  manager: redis
  # url: "redis://my-external-redis:6379/0"  # uncomment to use external Redis
  redis:
    enabled: true  # set to false if using external Redis

# Tika: the chart can auto-deploy Tika in-cluster
tika:
  enabled: true

# Ollama: disable if using external model APIs
ollama:
  enabled: false

# Storage: use object storage for multi-replica
persistence:
  provider: s3  # or "gcs" / "azure"
  s3:
    bucket: "my-openwebui-bucket"
    region: "us-east-1"
    accessKeyExistingSecret: "openwebui-s3-creds"
    accessKeyExistingAccessKey: "access-key"
    secretKeyExistingSecret: "openwebui-s3-creds"
    secretKeyExistingSecretKey: "secret-key"
  # Alternatively, use a shared filesystem (RWX PVC):
  # provider: local
  # accessModes:
  #   - ReadWriteMany
  # storageClass: "efs-sc"

# Ingress
ingress:
  enabled: true
  class: "nginx"
  host: "ai.example.com"
  tls: true
  existingSecret: "openwebui-tls"
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "open-webui-session"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"

# Remaining settings via env vars
extraEnvVars:
  - name: WEBUI_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: openwebui-secrets
        key: secret-key
  - name: VECTOR_DB
    value: "pgvector"
  - name: PGVECTOR_DB_URL
    valueFrom:
      secretKeyRef:
        name: openwebui-secrets
        key: database-url
  - name: UVICORN_WORKERS
    value: "1"
  - name: ENABLE_DB_MIGRATIONS
    value: "false"
  - name: RAG_EMBEDDING_ENGINE
    value: "openai"
```

## Scaling Strategy

- **Horizontal Pod Autoscaler (HPA)**: Scale on CPU or memory utilization. Keep `UVICORN_WORKERS=1` per pod and let Kubernetes manage the replica count.
- **Resource requests and limits**: Set appropriate CPU and memory requests to ensure the scheduler places pods correctly and the HPA has accurate metrics.
- **Pod disruption budgets**: Configure a PDB to ensure a minimum number of pods remain available during voluntary disruptions.

## Update Procedure

**Critical:** When running multiple replicas, follow this process for every update:

1. Scale the deployment to **1 replica**
2. Apply the new image version (with `ENABLE_DB_MIGRATIONS=true` on the single replica)
3. Wait for the pod to become **fully ready** (database migrations complete)
4. Scale back to your desired replica count (with `ENABLE_DB_MIGRATIONS=false`)

Skipping this process risks database corruption from concurrent migrations.

## Key Considerations

| Consideration | Detail |
| :--- | :--- |
| **Storage** | Use a **ReadWriteMany (RWX)** shared filesystem (EFS, CephFS, NFS) or object storage (S3, GCS, Azure Blob). ReadWriteOnce volumes will not work with multiple pods. |
| **Secrets** | Store credentials in Kubernetes Secrets and reference via `secretKeyRef`. Integrate with external secrets operators (External Secrets, Sealed Secrets) for GitOps workflows. |
| **Database** | Use a managed PostgreSQL service (RDS, Cloud SQL, Azure DB) for production. In-cluster PostgreSQL operators (CloudNativePG, Zalando) are viable but add operational burden. |
| **Redis** | A single Redis instance with `timeout 1800` and `maxclients 10000` is sufficient for most deployments. Redis Sentinel or Cluster is only needed if Redis itself must be highly available. |
| **Networking** | Keep all services in the same availability zone. Target < 2 ms database latency. Audit network policies to ensure pods can reach PostgreSQL, Redis, and storage backends. |
