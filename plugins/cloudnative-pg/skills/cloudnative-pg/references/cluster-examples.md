# Cluster Examples

## Single Instance (Homelab)

Minimal footprint, Rook Ceph persistence, no replicas.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: myapp-db
  namespace: databases
spec:
  instances: 1
  imageName: ghcr.io/cloudnative-pg/postgresql:17.2
  enableSuperuserAccess: true

  storage:
    size: 10Gi
    storageClass: ceph-block

  bootstrap:
    initdb:
      database: myapp
      owner: myapp
      postInitSQL:
        - CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

  postgresql:
    parameters:
      shared_buffers: "128MB"
      effective_cache_size: "384MB"
      work_mem: "4MB"
      maintenance_work_mem: "64MB"
      max_connections: "100"

  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
```

## HA Cluster (3 instances)

Primary + 2 replicas across different nodes.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: myapp-db
  namespace: databases
spec:
  instances: 3
  imageName: ghcr.io/cloudnative-pg/postgresql:17.2
  primaryUpdateStrategy: unsupervised

  storage:
    size: 20Gi
    storageClass: ceph-block

  walStorage:
    size: 5Gi
    storageClass: ceph-block

  bootstrap:
    initdb:
      database: myapp
      owner: myapp

  postgresql:
    parameters:
      shared_buffers: "256MB"
      effective_cache_size: "768MB"
      work_mem: "8MB"

  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"

  affinity:
    enablePodAntiAffinity: true
    topologyKey: kubernetes.io/hostname
```

## Separate WAL Storage

Place WAL on dedicated volume for better write performance. Recommended for HA clusters.

```yaml
spec:
  walStorage:
    size: 5Gi
    storageClass: ceph-block
```

## Storage Notes

- `ceph-block` StorageClass from Rook Ceph (RBD) works well
- Access mode is `ReadWriteOnce` (shared-nothing architecture)
- Storage can be expanded (never shrunk) if StorageClass allows `allowVolumeExpansion: true`
- Change `size` in Cluster spec to trigger PVC resize on all instances
- Without separate `walStorage`, WAL files share I/O with data files

## Ephemeral Storage

```yaml
spec:
  ephemeralVolumesSizeLimit:
    temporaryData: 1Gi
    shm: 256Mi  # Important for shared_buffers
```

## Bootstrap Methods

| Method | Use Case |
|--------|----------|
| `initdb` | Fresh database (default) |
| `recovery` | Restore from backup (object store or VolumeSnapshot) |
| `pg_basebackup` | Clone from live PostgreSQL instance |

For recovery bootstrap, see `references/restore-pitr.md`.
