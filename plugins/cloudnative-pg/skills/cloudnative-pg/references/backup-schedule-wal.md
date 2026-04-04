# Scheduled Backups and WAL Archiving

## ScheduledBackup

Uses **6-field cron** (seconds first, not standard 5-field):

```
seconds minutes hours day-of-month month day-of-week
```

### Example: Daily at midnight

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: myapp-db-daily
  namespace: databases
spec:
  schedule: "0 0 0 * * *"
  cluster:
    name: myapp-db
  method: plugin
  pluginConfiguration:
    name: barman-cloud.cloudnative-pg.io
    parameters:
      objectStoreName: s3-store
  immediate: true
  backupOwnerReference: self
```

### Key Fields

| Field | Description |
|-------|-------------|
| `schedule` | 6-field cron (with seconds!) |
| `immediate` | Trigger first backup on creation |
| `suspend` | Pause scheduling (no new backups) |
| `backupOwnerReference` | `none` (persist), `self` (delete with schedule), `cluster` (delete with cluster) |
| `method` | `plugin`, `volumeSnapshot`, or `barmanObjectStore` (deprecated) |

### Common Schedules

| Schedule | Cron |
|----------|------|
| Every day midnight | `0 0 0 * * *` |
| Every 6 hours | `0 0 */6 * * *` |
| Weekly Sunday 2am | `0 0 2 * * 0` |
| Every 12 hours | `0 0 */12 * * *` |

**Gotcha:** `"0 0 * * *"` (5-field) will fail silently. Always 6 fields.

## WAL Archiving

Required for Point-in-Time Recovery (PITR). Without it, recovery is limited to exact backup points.

WAL archiving is configured in the backup/ObjectStore config (see `references/backup-s3.md`):

```yaml
# In ObjectStore spec
spec:
  configuration:
    wal:
      compression: gzip
      maxParallel: 4
```

### archive_timeout

Default: **5 minutes**. Ensures WAL files are archived at least every 5 minutes, even under low write load. This sets an upper bound on RPO (Recovery Point Objective).

Override in PostgreSQL parameters if needed:

```yaml
spec:
  postgresql:
    parameters:
      archive_timeout: "300"  # 5 min default, in seconds
```

### Parallel Archiving

Set `maxParallel` based on network bandwidth. Useful for:
- High-write workloads generating many WAL files
- After downtime when WAL files have accumulated
- Default is 1; values of 4-8 are common for production

## Volume Snapshot Backups

Alternative to object store. Uses Kubernetes VolumeSnapshot API.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: myapp-db-snapshot
  namespace: databases
spec:
  schedule: "0 0 0 * * *"
  cluster:
    name: myapp-db
  method: volumeSnapshot
  online: true
```

### Hot vs Cold Snapshots

| Mode | `online` | Impact | Consistency |
|------|----------|--------|-------------|
| Hot (default) | `true` | No downtime | Via replication slot + WAL |
| Cold | `false` | Primary fenced during snapshot | Inherently consistent |

- Volume snapshots alone give recovery to snapshot point only
- Combine with WAL archiving for PITR between snapshots
- Requires CSI driver with snapshot support + VolumeSnapshotClass

## Retention

Configured on ObjectStore CRD (or legacy barmanObjectStore):

```yaml
retentionPolicy: "30d"  # Keep backups for 30 days
```

Uses "recovery window" concept: keeps the minimum set of backups + WAL needed to recover to any point within the window.
