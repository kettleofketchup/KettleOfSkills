# Recovery and Point-in-Time Recovery (PITR)

Recovery always **bootstraps a new cluster** from backup. It does not restore in-place.

## Recovery from Object Store

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: myapp-db-restored
  namespace: databases
spec:
  instances: 1
  storage:
    size: 10Gi
    storageClass: ceph-block

  bootstrap:
    recovery:
      source: s3-source

  externalClusters:
    - name: s3-source
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
      # serverName overrides folder name in object store (defaults to external cluster name)
      # serverName: myapp-db
```

## Recovery with PITR

Add `recoveryTarget` to recover to a specific point:

```yaml
spec:
  bootstrap:
    recovery:
      source: s3-source
      recoveryTarget:
        targetTime: "2026-03-05T10:30:00Z"
```

### PITR Target Options

| Target | Description |
|--------|-------------|
| `targetTime` | ISO 8601 timestamp (most common) |
| `targetLSN` | WAL log sequence number |
| `targetXID` | Transaction ID |
| `targetName` | Named restore point (requires `backupID`) |
| `targetImmediate` | End of base backup (requires `backupID`) |

Additional parameters:
- `exclusive: true` -- Stop **before** the target (default: inclusive)
- `targetTLI` -- Force specific timeline
- `backupID` -- Mandatory for `targetName`, `targetXID`, `targetImmediate`

## Recovery from Backup Object

Reference a specific Backup resource directly:

```yaml
spec:
  bootstrap:
    recovery:
      backup:
        name: myapp-db-manual
```

## Recovery from Volume Snapshot

```yaml
spec:
  bootstrap:
    recovery:
      volumeSnapshots:
        storage:
          name: myapp-db-pgdata-snapshot
          kind: VolumeSnapshot
          apiGroup: snapshot.storage.k8s.io
        walStorage:
          name: myapp-db-wal-snapshot
          kind: VolumeSnapshot
          apiGroup: snapshot.storage.k8s.io
```

## Clone via pg_basebackup

Clone a live cluster (streaming, no PITR):

```yaml
spec:
  bootstrap:
    pg_basebackup:
      source: source-cluster
  externalClusters:
    - name: source-cluster
      connectionParameters:
        host: myapp-db-rw.databases.svc
        user: streaming_replica
        dbname: myapp
      sslMode: verify-full
```

## Key Points

- Recovery creates a new, independent cluster
- Without `recoveryTarget`, replays all available WAL (latest point)
- PITR requires WAL archiving to be configured on the source cluster
- `serverName` in externalClusters controls the backup folder lookup path
- Test recovery procedures regularly
