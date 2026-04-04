---
name: cloudnative-pg
description: CloudNativePG (CNPG) Kubernetes operator for PostgreSQL. Use when deploying PostgreSQL clusters on Kubernetes, creating Cluster CRDs, configuring PgBouncer connection pooling (Pooler), setting up S3/MinIO backups with Barman Cloud Plugin, WAL archiving, scheduled backups, point-in-time recovery (PITR), declarative role management, Prometheus monitoring, failover/switchover, hibernating clusters, or troubleshooting CNPG issues. Covers single-instance homelab and HA multi-replica patterns with Rook Ceph storage.
---

# CloudNativePG (CNPG)

Kubernetes operator for PostgreSQL. Shared-nothing architecture: each instance has dedicated storage, managed directly by operator (not StatefulSet).

## Install Operator

```bash
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo update
helm install cnpg cnpg/cloudnative-pg -n cnpg-system --create-namespace
kubectl -n cnpg-system wait --for=condition=ready pod -l app.kubernetes.io/name=cloudnative-pg --timeout=300s
```

Install kubectl plugin: `curl -sSfL https://github.com/cloudnative-pg/cloudnative-pg/raw/main/hack/install-cnpg-plugin.sh | sudo sh -s -- -b /usr/local/bin`

## Quick Start - Single Instance

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: my-db
  namespace: databases
spec:
  instances: 1
  storage:
    size: 10Gi
    storageClass: ceph-block
  bootstrap:
    initdb:
      database: app
      owner: app
```

Services created: `my-db-rw` (primary), `my-db-ro` (replicas), `my-db-r` (any readable).
Credentials in Secrets: `my-db-app` (app user), `my-db-superuser` (if enabled).

## Quick Start - HA Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: my-db
spec:
  instances: 3
  storage:
    size: 20Gi
    storageClass: ceph-block
  postgresql:
    parameters:
      shared_buffers: "256MB"
      effective_cache_size: "768MB"
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
```

## Key Concepts

- Operator manages Pods directly (no StatefulSet) for fine-grained failover control
- Automated failover: promotes most up-to-date replica if primary fails
- TLS auto-managed: self-signed CA, 90-day certs, auto-renewed
- Superuser disabled by default; enable with `enableSuperuserAccess: true`
- Default bootstrap creates `app` database owned by `app` user
- ALTER SYSTEM disabled by default (all config via Cluster spec)
- PodDisruptionBudgets auto-created

## Verify

```bash
kubectl cnpg status my-db -n databases
kubectl get cluster my-db -n databases
kubectl get pods -l cnpg.io/clusterName=my-db -n databases -L role -o wide
```

## Connect

```bash
# Port-forward
kubectl port-forward svc/my-db-rw 5432:5432 -n databases
# From within cluster
psql "host=my-db-rw.databases.svc dbname=app user=app"
```

## References

- `references/cluster-examples.md` - Detailed single + HA cluster manifests
- `references/backup-s3.md` - Barman Cloud Plugin, S3/MinIO object store setup
- `references/backup-schedule-wal.md` - Scheduled backups, WAL archiving, retention
- `references/restore-pitr.md` - Recovery bootstrap, PITR targets
- `references/pooler-pgbouncer.md` - PgBouncer connection pooling
- `references/monitoring.md` - Prometheus metrics, PodMonitor, custom queries
- `references/roles-pgconfig.md` - Declarative roles, PostgreSQL configuration
- `references/kubectl-cnpg.md` - Plugin commands reference
- `references/operations.md` - Failover, switchover, hibernate, maintenance
- `references/troubleshooting.md` - Diagnostics, common issues
