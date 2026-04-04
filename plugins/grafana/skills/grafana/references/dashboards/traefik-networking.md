# Traefik / Networking Dashboard

uid: `traefik-networking`, folder: `Networking`

Requires Traefik `metrics.prometheus.enabled: true` (already set in cluster).

## Variables

```
$datasource: type=datasource, query=prometheus
$entrypoint: label_values(traefik_entrypoint_requests_total, entrypoint), multi, includeAll
$service: label_values(traefik_service_requests_total, service), multi, includeAll
```

## Row 1: Overview Stats (y=0, h=4)

| Panel | w | Query | Config |
|-------|---|-------|--------|
| Requests/sec | 4 | `sum(rate(traefik_entrypoint_requests_total[5m]))` | -- |
| 4xx Rate | 4 | `sum(rate(traefik_entrypoint_requests_total{code=~"4.."}[5m]))` | green<1, yellow<10, red |
| 5xx Rate | 4 | `sum(rate(traefik_entrypoint_requests_total{code=~"5.."}[5m]))` | green<0.1, yellow<1, red |
| Open Connections | 4 | `sum(traefik_open_connections)` | -- |
| Config Reloads | 4 | `sum(traefik_config_reloads_total)` | -- |
| TLS Cert Expiry | 4 | `min(traefik_tls_certs_not_after) - time()` | unit: s, green>30d, yellow>7d, red |

## Row 2: Request Rates (y=4, h=8)

**Requests/sec by Entrypoint** (w=12, timeseries):
```promql
sum by (entrypoint) (rate(traefik_entrypoint_requests_total[5m]))
```

**Response Code Distribution** (w=12, timeseries, stacked):
```promql
sum by (code) (rate(traefik_entrypoint_requests_total{entrypoint=~"$entrypoint"}[5m]))
```
Color overrides: 2xx=green, 3xx=blue, 4xx=yellow, 5xx=red

## Row 3: Latency (y=12, h=8)

**Entrypoint Latency p50/p95/p99** (w=12, timeseries, unit: seconds):
```promql
histogram_quantile(0.50, sum by (le) (rate(traefik_entrypoint_request_duration_seconds_bucket{entrypoint=~"$entrypoint"}[5m])))
histogram_quantile(0.95, sum by (le) (rate(traefik_entrypoint_request_duration_seconds_bucket{entrypoint=~"$entrypoint"}[5m])))
histogram_quantile(0.99, sum by (le) (rate(traefik_entrypoint_request_duration_seconds_bucket{entrypoint=~"$entrypoint"}[5m])))
```

**Service Latency p95** (w=12, timeseries, unit: seconds):
```promql
histogram_quantile(0.95, sum by (le, service) (rate(traefik_service_request_duration_seconds_bucket[5m])))
```

## Row 4: Service Details (y=20, h=8)

**Requests by Service** (w=12, timeseries):
```promql
sum by (service) (rate(traefik_service_requests_total[5m]))
```

**Service Error Rate %** (w=12, timeseries):
```promql
sum by (service) (rate(traefik_service_requests_total{code=~"5.."}[5m]))
  / sum by (service) (rate(traefik_service_requests_total[5m])) * 100
```
Thresholds: green<1, yellow<5, red

## Row 5: Connections & Bytes (y=28, h=8)

**Open Connections** (w=8, timeseries):
```promql
traefik_open_connections{entrypoint=~"$entrypoint"}
```

**Bytes In per Service** (w=8, timeseries, unit: Bps):
```promql
sum by (service) (rate(traefik_service_requests_bytes_total[5m]))
```

**Bytes Out per Service** (w=8, timeseries, unit: Bps):
```promql
sum by (service) (rate(traefik_service_responses_bytes_total[5m]))
```

## Row 6: Service Health (y=36, h=8)

**Server Status** (w=12, table):
```promql
traefik_service_server_up
```
Labels: `service`, `url`. Mappings: 1=Up, 0=Down. Thresholds: green=1, red=0

**Service Retries** (w=12, timeseries):
```promql
sum by (service) (rate(traefik_service_retries_total[5m]))
```

## Key Metrics Reference

```
# Global
traefik_config_reloads_total           traefik_config_last_reload_success
traefik_open_connections{entrypoint,protocol}
traefik_tls_certs_not_after{cn,sans}

# Entrypoint (addEntryPointsLabels=true)
traefik_entrypoint_requests_total{code,method,protocol,entrypoint}
traefik_entrypoint_request_duration_seconds_bucket{code,method,entrypoint}  # histogram
traefik_entrypoint_requests_bytes_total
traefik_entrypoint_responses_bytes_total

# Router (addRoutersLabels=true)
traefik_router_requests_total{code,method,router,service}
traefik_router_request_duration_seconds_bucket  # histogram

# Service (addServicesLabels=true)
traefik_service_requests_total{code,method,service}
traefik_service_request_duration_seconds_bucket  # histogram
traefik_service_retries_total{service}
traefik_service_server_up{service,url}  # 1=up, 0=down
traefik_service_requests_bytes_total
traefik_service_responses_bytes_total
```
