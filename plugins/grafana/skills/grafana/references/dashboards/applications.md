# Application Dashboards — CNPG and ArgoCD

For Authentik dashboard, see [applications-authentik.md](applications-authentik.md).

## CNPG PostgreSQL

uid: `cnpg-postgresql`, folder: `Applications`. Community dashboard: `20417`

### Variables
```
$namespace: label_values(cnpg_collector_up, namespace)
$cluster: label_values(cnpg_collector_up{namespace="$namespace"}, cluster)
```

### Panels

**Row 1: Overview** (stat, y=0, h=4)

| Panel | Query |
|-------|-------|
| Instances Up | `count(cnpg_collector_up{namespace="$namespace",cluster="$cluster"} == 1)` |
| Replication Lag | `max(cnpg_pg_replication_lag{namespace="$namespace",cluster="$cluster"})` (unit:s, green<1, red>5) |
| Streaming Replicas | `cnpg_pg_replication_streaming_replicas{...}` |
| Primary/Replica | `cnpg_pg_replication_in_recovery{...}` (map: 0=Primary, 1=Replica) |

**Row 2: Database Size and Connections** (timeseries, y=4, h=8)
```promql
cnpg_pg_database_size_bytes{namespace="$namespace",cluster="$cluster"}  # (w=12, unit: bytes)
sum by (state) (cnpg_backends_total{namespace="$namespace",cluster="$cluster"})  # (w=12, stacked)
```

**Row 3: Transactions** (timeseries, y=12, h=8)
```promql
sum(rate(cnpg_pg_stat_database_xact_commit{namespace="$namespace",cluster="$cluster"}[5m]))
sum(rate(cnpg_pg_stat_database_xact_rollback{...}[5m]))
# Cache Hit Ratio (thresholds: red<0.9, green>0.99)
sum(rate(cnpg_pg_stat_database_blks_hit{...}[5m]))
  / (sum(rate(cnpg_pg_stat_database_blks_hit{...}[5m]))
  + sum(rate(cnpg_pg_stat_database_blks_read{...}[5m])))
```

**Row 4: WAL and Archiver** (timeseries, y=20, h=8)
```promql
rate(cnpg_pg_stat_archiver_archived_count{...}[5m])
rate(cnpg_pg_stat_archiver_failed_count{...}[5m])
cnpg_pg_replication_slots_pg_wal_lsn_diff{...}
```

### Key Metrics
```
cnpg_collector_up  cnpg_pg_replication_lag  cnpg_pg_replication_in_recovery
cnpg_pg_database_size_bytes{datname}  cnpg_backends_total{state}
cnpg_pg_stat_database_xact_commit  cnpg_pg_stat_database_xact_rollback
cnpg_pg_stat_database_blks_hit  cnpg_pg_stat_database_blks_read
cnpg_pg_stat_archiver_archived_count  cnpg_pg_stat_archiver_failed_count
cnpg_pg_replication_slots_pg_wal_lsn_diff{slot_name}
```

---

## ArgoCD

uid: `argocd-overview`, folder: `Applications`

### Variables
```
$namespace: label_values(argocd_app_info, namespace)
$project: label_values(argocd_app_info, project), multi, includeAll
```

### Panels

**Row 1: App Status** (stat, y=0, h=4)

| Panel | Query | Config |
|-------|-------|--------|
| Total Apps | `count(argocd_app_info)` | -- |
| Healthy | `count(argocd_app_info{health_status="Healthy"})` | green |
| Degraded | `count(argocd_app_info{health_status="Degraded"})` | green=0, red>0 |
| Synced | `count(argocd_app_info{sync_status="Synced"})` | -- |
| OutOfSync | `count(argocd_app_info{sync_status="OutOfSync"})` | green=0, yellow>0 |

**Row 2: App Details** (table, y=4, h=8, w=24)
```promql
argocd_app_info   # columns: name, project, sync_status, health_status, repo
```

**Row 3: Sync and Reconciliation** (timeseries, y=12, h=8)
```promql
sum(rate(argocd_app_sync_total{phase="Succeeded"}[5m]))  # (w=12, stacked)
sum(rate(argocd_app_sync_total{phase="Failed"}[5m]))
histogram_quantile(0.95, sum by (le) (rate(argocd_app_reconcile_bucket[5m])))  # p95 (w=12, unit: s)
```

**Row 4: Git and API** (timeseries, y=20, h=8)
```promql
sum by (repo) (rate(argocd_git_request_total[5m]))      # (w=12)
sum by (name) (rate(argocd_app_k8s_request_total[5m]))  # (w=12)
```

### Key Metrics
```
argocd_app_info{name,sync_status,health_status,project,repo}
argocd_app_sync_total{name,phase}  argocd_app_reconcile_bucket
argocd_git_request_total{repo}  argocd_app_k8s_request_total{name,verb}
```
