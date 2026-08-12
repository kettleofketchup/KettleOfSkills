# Datasources — PostgreSQL and Cross-Signal Correlation

## PostgreSQL (CNPG) Datasource

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: datasource-postgresql
  namespace: monitoring
  labels:
    grafana_datasource: "1"
data:
  postgresql.yaml: |
    apiVersion: 1
    datasources:
      - name: PostgreSQL
        type: postgres
        url: cluster-name-rw.namespace.svc:5432
        user: grafana_reader
        jsonData:
          database: database-name
          sslmode: require
          maxOpenConns: 5
          maxIdleConns: 2
        secureJsonData:
          password: "$GRAFANA_PG_PASSWORD"
```

### CNPG Read-Only User

```sql
CREATE ROLE grafana_reader WITH LOGIN PASSWORD '...';
GRANT CONNECT ON DATABASE mydb TO grafana_reader;
GRANT USAGE ON SCHEMA public TO grafana_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_reader;
```

Alternative to ConfigMap sidecar: use `grafana.additionalDataSources` in kube-prometheus-stack Helm values.

## Cross-Signal Correlation

### Bidirectional Loki-Tempo Linking

Both directions require explicit `uid` on each datasource.

**Loki to Tempo** (derivedFields on Loki datasource):
```yaml
jsonData:
  derivedFields:
    - datasourceUid: tempo
      matcherRegex: '"traceId":"(\\w+)"'
      name: TraceID
      url: "$${__value.raw}"
```

**Tempo to Loki** (tracesToLogs on Tempo datasource):
```yaml
jsonData:
  tracesToLogs:
    datasourceUid: loki
    filterByTraceID: true
    mapTagNamesEnabled: true
    mappedTags:
      - key: k8s.namespace.name
        value: namespace
      - key: k8s.pod.name
        value: pod
```

### OTEL Collector Spanmetrics

For `tracesToMetrics` and `serviceMap` to work, the OTEL Collector needs a `spanmetrics` connector that generates RED metrics from traces:

```yaml
config:
  connectors:
    spanmetrics:
      histogram:
        explicit:
          buckets: [5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s]
      dimensions:
        - name: http.method
        - name: http.status_code
      namespace: traces.spanmetrics
  service:
    pipelines:
      traces:
        exporters: [otlp/tempo, spanmetrics]
      metrics/spanmetrics:
        receivers: [spanmetrics]
        exporters: [prometheusremotewrite]
```

Without this, Tempo's service map and trace-to-metrics links produce empty results.

## Datasource via additionalDataSources (Helm)

All datasources can also be provisioned via Helm values instead of separate ConfigMaps:

```yaml
grafana:
  additionalDataSources:
    - name: Loki
      type: loki
      uid: loki
      url: http://loki:3100
      access: proxy
    - name: Tempo
      type: tempo
      uid: tempo
      url: http://tempo:3200
      access: proxy
      jsonData:
        tracesToLogs:
          datasourceUid: loki
          filterByTraceID: true
        serviceMap:
          datasourceUid: prometheus
        nodeGraph:
          enabled: true
```

This keeps all datasource config in a single values file without requiring separate ConfigMap management.
