# Datasource Configuration

## Explicit Datasource UIDs (Critical)

Always set explicit `uid` on datasources. Without explicit UIDs, Grafana auto-generates random ones and cross-references (`datasourceUid: tempo`, `datasourceUid: loki`) silently break.

```yaml
additionalDataSources:
  - name: Tempo
    type: tempo
    uid: tempo          # explicit — referenced by Loki derivedFields
    url: http://tempo:3200
  - name: Loki
    type: loki
    uid: loki           # explicit — referenced by Tempo tracesToLogs
    url: http://loki:3100
```

## Prometheus (Built-in)

kube-prometheus-stack auto-configures Prometheus as default datasource. Default UID is `prometheus`. Set `grafana.sidecar.datasources.defaultDatasourceEnabled: true` (on by default) to auto-create it.

## Loki (Log Aggregation)

```bash
helm upgrade --install loki grafana/loki -n monitoring -f loki-values.yaml
```

Minimal single-binary values for small clusters:
```yaml
loki:
  auth_enabled: false
  commonConfig:
    replication_factor: 1
  storage:
    type: filesystem
  schemaConfig:
    configs:
      - from: "2024-01-01"
        store: tsdb
        object_store: filesystem
        schema: v13
        index:
          prefix: index_
          period: 24h
singleBinary:
  replicas: 1
  persistence:
    enabled: true
    storageClass: ceph-block
    size: 20Gi
```

### Log Collection Agent (Alloy)

Deploy Grafana Alloy (successor to Promtail): `helm upgrade --install alloy grafana/alloy -n monitoring -f alloy-values.yaml`

```yaml
# alloy-values.yaml — minimal pod log collection
alloy:
  configMap:
    content: |
      discovery.kubernetes "pods" { role = "pod" }
      loki.source.kubernetes "pods" {
        targets = discovery.kubernetes.pods.targets
        forward_to = [loki.write.default.receiver]
      }
      loki.write "default" {
        endpoint { url = "http://loki:3100/loki/api/v1/push" }
      }
```

### Loki Datasource ConfigMap

```yaml
# ConfigMap with grafana_datasource: "1" label
data:
  loki.yaml: |
    apiVersion: 1
    datasources:
      - name: Loki
        type: loki
        uid: loki
        url: http://loki:3100
        access: proxy
        isDefault: false
        jsonData:
          derivedFields:
            - name: TraceID
              matcherRegex: "traceID=(\\w+)"
              url: "$${__value.raw}"
              datasourceUid: tempo
```

## Tempo (Distributed Tracing)

```bash
helm upgrade --install tempo grafana/tempo -n monitoring -f tempo-values.yaml
```

```yaml
tempo:
  storage:
    trace:
      backend: local
      local:
        path: /var/tempo/traces
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318
persistence:
  enabled: true
  storageClassName: ceph-block
  size: 10Gi
```

### Tempo Datasource ConfigMap

```yaml
data:
  tempo.yaml: |
    apiVersion: 1
    datasources:
      - name: Tempo
        type: tempo
        uid: tempo
        url: http://tempo:3100
        access: proxy
        jsonData:
          tracesToMetrics:
            datasourceUid: prometheus
          tracesToLogs:
            datasourceUid: loki
            filterByTraceID: true
          serviceMap:
            datasourceUid: prometheus
          nodeGraph:
            enabled: true
```

For PostgreSQL datasource and cross-signal correlation config, see [datasources-postgresql-correlation.md](datasources-postgresql-correlation.md).
