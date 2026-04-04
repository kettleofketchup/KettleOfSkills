# Backup to S3-Compatible Storage

## Deprecation Notice

In-tree `barmanObjectStore` is deprecated in v1.26, removed in v1.28. Use the **Barman Cloud Plugin** with `ObjectStore` CRD instead.

## Setup with Barman Cloud Plugin

### 1. Install Plugin

```bash
helm install barman-cloud cnpg/barman-cloud-plugin -n cnpg-system
```

### 2. Create S3 Credentials Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: s3-backup-creds
  namespace: databases
type: Opaque
stringData:
  ACCESS_KEY_ID: "minioadmin"
  ACCESS_SECRET_KEY: "minioadmin"
```

### 3. Create ObjectStore

```yaml
apiVersion: barmancloud.cnpg.io/v1
kind: ObjectStore
metadata:
  name: s3-store
  namespace: databases
spec:
  configuration:
    destinationPath: s3://pg-backups/myapp-db
    endpointURL: https://minio.storage.svc:9000
    s3Credentials:
      accessKeyId:
        name: s3-backup-creds
        key: ACCESS_KEY_ID
      secretAccessKey:
        name: s3-backup-creds
        key: ACCESS_SECRET_KEY
    wal:
      compression: gzip
      maxParallel: 4
    data:
      compression: gzip
    # For self-signed MinIO certs:
    endpointCA:
      name: minio-ca-secret
      key: ca.crt
  retentionPolicy: "30d"
```

### 4. Reference in Cluster

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: myapp-db
spec:
  instances: 1
  storage:
    size: 10Gi
    storageClass: ceph-block
  backup:
    pluginConfiguration:
      - name: barman-cloud.cloudnative-pg.io
        parameters:
          objectStoreName: s3-store
```

## Legacy In-Tree Config (pre v1.26)

```yaml
spec:
  backup:
    barmanObjectStore:
      destinationPath: s3://pg-backups/myapp-db
      endpointURL: https://minio.storage.svc:9000
      s3Credentials:
        accessKeyId:
          name: s3-backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: s3-backup-creds
          key: ACCESS_SECRET_KEY
      wal:
        compression: gzip
        maxParallel: 4
      data:
        compression: gzip
    retentionPolicy: "30d"
```

## Take Manual Backup

```bash
kubectl cnpg backup myapp-db -n databases
# Or with YAML:
```

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Backup
metadata:
  name: myapp-db-manual
  namespace: databases
spec:
  method: plugin
  cluster:
    name: myapp-db
  pluginConfiguration:
    name: barman-cloud.cloudnative-pg.io
    parameters:
      objectStoreName: s3-store
```

## Key Points

- `endpointCA` required for self-signed/private CA HTTPS endpoints (common with MinIO)
- Compression options: `gzip`, `bzip2`, `snappy` (independent for WAL and data)
- `maxParallel` for WAL: increase for high-write workloads (default: 1)
- Retention uses "recovery window" -- keeps backups needed to recover within the window
