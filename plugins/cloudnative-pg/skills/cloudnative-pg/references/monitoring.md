# Prometheus Monitoring

## Metrics Endpoints

- Each PostgreSQL instance: port **9187**, path `/metrics`
- Operator itself: port **8080**

## Enable Default Metrics

CNPG ships default metrics in ConfigMap `cnpg-default-monitoring`. Enable on cluster:

```yaml
spec:
  monitoring:
    enablePodMonitor: false  # Create PodMonitor manually for full control
```

## PodMonitor (Recommended)

Create manually for full control over monitoring config:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: myapp-db
  namespace: databases
  labels:
    release: prometheus  # Match your Prometheus operator selector
spec:
  selector:
    matchLabels:
      cnpg.io/clusterName: myapp-db
  podMetricsEndpoints:
    - port: metrics
```

## Custom Metrics

Define via ConfigMap, reference in Cluster:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-db-metrics
  namespace: databases
  labels:
    cnpg.io/reload: "true"  # Auto-reload on change
data:
  custom-queries: |
    pg_database_size:
      query: "SELECT datname, pg_database_size(datname) as size_bytes FROM pg_database WHERE datistemplate = false"
      metrics:
        - datname:
            usage: "LABEL"
            description: "Database name"
        - size_bytes:
            usage: "GAUGE"
            description: "Database size in bytes"
      target_databases:
        - "*"
```

Reference in Cluster:

```yaml
spec:
  monitoring:
    customQueriesConfigMap:
      - name: myapp-db-metrics
        key: custom-queries
```

## Key Metrics to Monitor

| Metric | Description |
|--------|-------------|
| `cnpg_collector_up` | Instance health |
| `cnpg_backends_total` | Active connections |
| `cnpg_pg_replication_lag` | Replication lag (seconds) |
| `cnpg_pg_database_size_bytes` | Database size |
| `cnpg_pg_stat_archiver_archived_count` | WAL files archived |
| `cnpg_pg_stat_archiver_failed_count` | Failed WAL archiving |

## Key Points

- Custom queries ConfigMap/Secret must be in same namespace as Cluster
- `target_databases` defaults to bootstrap database; use `["*"]` for all databases
- Add `cnpg.io/reload: "true"` label to ConfigMaps for auto-reload on change
- Grafana dashboard available from CNPG project
- Metrics format: `cnpg_<MetricName>_<ColumnName>{<LabelColumnName>=<LabelColumnValue>}`
