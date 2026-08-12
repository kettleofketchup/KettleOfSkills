# Application Dashboards — Authentik

For CNPG and ArgoCD dashboards, see [applications.md](applications.md).

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
histogram_quantile(0.95, sum by (le) (rate(authentik_main_request_duration_seconds_bucket[5m])))
histogram_quantile(0.99, sum by (le) (rate(authentik_main_request_duration_seconds_bucket[5m])))

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

## Authentik ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: authentik
  namespace: authentik
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: authentik
      app.kubernetes.io/component: server
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

For OIDC/SSO integration with Grafana, see [../authentik-oidc.md](../authentik-oidc.md).
