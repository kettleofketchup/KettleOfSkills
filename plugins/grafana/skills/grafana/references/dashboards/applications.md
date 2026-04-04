# Application Dashboards

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

**Row 2: Database Size & Connections** (timeseries, y=4, h=8)
```promql
# Size (w=12, unit: bytes)
cnpg_pg_database_size_bytes{namespace="$namespace",cluster="$cluster"}

# Connections by state (w=12, stacked)
sum by (state) (cnpg_backends_total{namespace="$namespace",cluster="$cluster"})
```

**Row 3: Transactions** (timeseries, y=12, h=8)
```promql
# Commits vs Rollbacks (w=12)
sum(rate(cnpg_pg_stat_database_xact_commit{namespace="$namespace",cluster="$cluster"}[5m]))
sum(rate(cnpg_pg_stat_database_xact_rollback{...}[5m]))

# Cache Hit Ratio (w=12, thresholds: red<0.9, green>0.99)
sum(rate(cnpg_pg_stat_database_blks_hit{...}[5m]))
  / (sum(rate(cnpg_pg_stat_database_blks_hit{...}[5m]))
  + sum(rate(cnpg_pg_stat_database_blks_read{...}[5m])))
```

**Row 4: WAL & Archiver** (timeseries, y=20, h=8)
```promql
rate(cnpg_pg_stat_archiver_archived_count{...}[5m])  # Archived WALs
rate(cnpg_pg_stat_archiver_failed_count{...}[5m])    # Failed archival
cnpg_pg_replication_slots_pg_wal_lsn_diff{...}       # Slot lag (bytes)
```

### Key Metrics
```
cnpg_collector_up  cnpg_pg_replication_lag  cnpg_pg_replication_in_recovery
cnpg_pg_database_size_bytes{datname}  cnpg_backends_total{state}
cnpg_pg_stat_database_xact_commit  cnpg_pg_stat_database_xact_rollback
cnpg_pg_stat_database_blks_hit  cnpg_pg_stat_database_blks_read
cnpg_pg_stat_database_tup_inserted/updated/deleted/fetched
cnpg_pg_stat_database_temp_files  cnpg_pg_stat_database_deadlocks
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

**Row 3: Sync & Reconciliation** (timeseries, y=12, h=8)
```promql
# Sync operations (w=12, stacked)
sum(rate(argocd_app_sync_total{phase="Succeeded"}[5m]))
sum(rate(argocd_app_sync_total{phase="Failed"}[5m]))

# Reconciliation p95 (w=12, unit: seconds)
histogram_quantile(0.95, sum by (le) (rate(argocd_app_reconcile_bucket[5m])))
```

**Row 4: Git & API** (timeseries, y=20, h=8)
```promql
sum by (repo) (rate(argocd_git_request_total[5m]))     # Git requests (w=12)
sum by (name) (rate(argocd_app_k8s_request_total[5m])) # K8s API (w=12)
```

### Key Metrics
```
argocd_app_info{name,sync_status,health_status,project,repo}
argocd_app_sync_total{name,phase}  argocd_app_reconcile_bucket
argocd_git_request_total{repo}  argocd_app_k8s_request_total{name,verb}
argocd_cluster_connection_status  argocd_cluster_api_resource_objects
```

---

## Authentik

uid: `authentik-overview`, folder: `Applications`

### Variables
```
$datasource: type=datasource, query=prometheus
```

### Panels

**Row 1: Overview** (stat, y=0, h=4)

| Panel | Query |
|-------|-------|
| Server Request Rate | `sum(rate(authentik_main_request_duration_seconds_count[5m]))` |
| Proxy Request Rate | `sum(rate(authentik_outpost_proxy_request_duration_seconds_count[5m]))` |
| Django Request Rate | `sum(rate(django_http_requests_total_by_method_total[5m]))` |

**Row 2: Latency** (timeseries, y=4, h=8)
```promql
# Server latency p50/p95/p99 (w=12, unit: seconds)
histogram_quantile(0.50, sum by (le) (rate(authentik_main_request_duration_seconds_bucket[5m])))
histogram_quantile(0.95, ...)
histogram_quantile(0.99, ...)

# Django responses by status (w=12, stacked)
sum by (status) (rate(django_http_responses_total_by_status_total[5m]))
```

**Row 3: HTTP Details** (timeseries, y=12, h=8)
```promql
# Requests by method (w=12)
sum by (method) (rate(django_http_requests_total_by_method_total[5m]))

# Proxy outpost latency p95 (w=12)
histogram_quantile(0.95, sum by (le) (rate(authentik_outpost_proxy_request_duration_seconds_bucket[5m])))
```

### Key Metrics
```
authentik_main_request_duration_seconds_bucket  # histogram
authentik_outpost_proxy_request_duration_seconds_bucket
django_http_requests_total_by_method_total{method,view}
django_http_responses_total_by_status_total{status}
authentik_outpost_ldap_request_duration_seconds_bucket{type}
authentik_outpost_flow_timing_get_seconds_bucket
```
