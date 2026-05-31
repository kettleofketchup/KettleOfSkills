---
name: grafana
last_updated: 2026-03-23
description: "Grafana observability on Kubernetes (kube-prometheus-stack). This skill should be used when deploying Grafana/Prometheus/Loki/Tempo, building dashboards, ServiceMonitors, OIDC, or trace correlation."
---

# Grafana Observability Stack

Full observability stack for self-hosted Kubernetes via `kube-prometheus-stack` Helm chart. Bundles Grafana, Prometheus, Alertmanager, node-exporter, kube-state-metrics, and default recording/alerting rules.

## Deployment

### kube-prometheus-stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -f values.yaml -n monitoring --create-namespace
```

For ArgoCD app-of-apps pattern, Helm values structure, CRD management, and namespace configuration, see [kube-prometheus-stack.md](references/kube-prometheus-stack.md).

### Additional Stack Components

Loki (logs), Tempo (traces) deploy as separate Helm charts in the same namespace:
- `grafana/loki` - log aggregation (Promtail/Alloy as agent)
- `grafana/tempo` - distributed tracing
- See [datasources.md](references/datasources.md) for configuration

## Task Reference

### Querying logs from the CLI
Pull and parse Loki logs at the terminal with `logcli` (Grafana's dedicated Loki
CLI — real `--since 7d`, `jsonl` output, `--tail`). Share one Grafana
service-account (bot) token with `gcx`, or point `LOKI_ADDR` at the datasource
proxy with a bearer token; covers `gcx` session reuse and when to pick
`gcx logs query` vs `logcli`, plus error breakdowns and trace correlation.
- See [logcli.md](references/logcli.md)

### Dashboard Creation
Build Grafana dashboards: JSON model structure, panel types (timeseries, stat, gauge, table, logs, heatmap), template variables, PromQL/LogQL query patterns.

**Prefer the Grafana Foundation SDK over hand-written JSON for new
dashboards.** It's Grafana's official Python (also Go, Java, TypeScript,
PHP) library that emits dashboard JSON typed against the same CUE
schemas Grafana itself uses internally — so the output validates
against Grafana Cloud's schema by construction instead of relying on
hand-curated validators that drift behind Grafana releases. See
[dashboard-foundation-sdk.md](references/dashboard-foundation-sdk.md)
for install, build patterns (DashboardBuilder + RowBuilder + panel
builders), V1-vs-V2 (Scenes) model selection, and the export-to-JSON
flow used by the reference impl in
`docs/dev/telemetry/dashboards/gen_dashboard.py`.

- Provisioning via ConfigMap sidecar (label: `grafana_dashboard: "1"`)
- Git-based provisioning via ArgoCD kustomize overlay
- See [dashboard-creation.md](references/dashboard-creation.md)

### Datasource Configuration
Configure Prometheus, Loki, Tempo, and PostgreSQL datasources.
- Provisioned via Helm values (`additionalDataSources`) or ConfigMap sidecar
- Tempo-to-Prometheus exemplar linking, Loki derived fields for trace correlation
- See [datasources.md](references/datasources.md)

### ServiceMonitors & PodMonitors
Expose application metrics for Prometheus scraping.
- ServiceMonitor for Service-backed endpoints (Traefik, ArgoCD, CNPG, Rook-Ceph)
- PodMonitor for direct pod scraping
- PrometheusRule for custom alerting/recording rules
- See [servicemonitors.md](references/servicemonitors.md)

### Authentik OIDC Integration
SSO login via Authentik OAuth2/OIDC provider.
- Grafana `auth.generic_oauth` configuration via Helm values
- Role mapping: Authentik groups to Grafana roles (Admin/Editor/Viewer)
- See [authentik-oidc.md](references/authentik-oidc.md)

## Domain-Specific Dashboards

Detailed panel layouts, PromQL/LogQL queries, and metric references per domain:

| Dashboard | Reference |
|-----------|-----------|
| Kubernetes cluster health | [dashboards/cluster-health.md](references/dashboards/cluster-health.md) |
| Ceph storage monitoring | [dashboards/ceph-storage.md](references/dashboards/ceph-storage.md) |
| Traefik ingress/networking | [dashboards/traefik-networking.md](references/dashboards/traefik-networking.md) |
| CNPG, ArgoCD, Authentik | [dashboards/applications.md](references/dashboards/applications.md) |
| LogQL syntax reference | [dashboards/logs-logql.md](references/dashboards/logs-logql.md) |
| Log dashboards, alerting, app queries | [dashboards/logs-dashboards.md](references/dashboards/logs-dashboards.md) |

## Key Patterns

- kube-prometheus-stack CRDs must sync before the chart — use `ServerSideApply=true` and separate CRD app or `crds.enabled: true`
- Dashboard ConfigMaps must have label `grafana_dashboard: "1"` for sidecar pickup
- Datasource ConfigMaps need label `grafana_datasource: "1"`
- Cross-namespace ServiceMonitor scraping requires `prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues: false`
- Grafana persistent storage: use `persistence.enabled: true` with appropriate StorageClass for sqlite DB (dashboards provisioned from ConfigMaps survive restarts regardless)

## Dashboard Review (Pre-Deploy Validation)

After editing any dashboard JSON, run the review script before commit. Catches the bugs that produce silent HTTP 400 from Grafana's `/api/ds/query` endpoint and cascading `ERR_NETWORK_CHANGED` in the browser:

| Bug class | Symptom |
|-----------|---------|
| **Paren imbalance in LogQL** | "parse error: unexpected $end" — `topk(N, sum by (X) (count_over_time(...)))` needs THREE trailing `)`s; one missing is invisible at JSON-render but fatal at parse |
| **Over-escaped regex** | Dashboard returns no data — `\\\\.` in JSON source decodes to `\\.` in memory, in LogQL backticks that's regex `\\.` (literal-backslash-then-any-char), not `\.` (literal dot). Halve the backslashes if you see `\\\\\\\\` anywhere |
| **Mixed-datasource broken join** | Empty table — Loki returns `client`, Prometheus returns `pod_ip`; need a `renameByRegex` step BEFORE `joinByField` to align them |
| **Unmatched template variable** | Empty/null filter values — panel references `$source` but dashboard only declares `$cluster` |
| **Unbalanced backtick raw string** | Parser treats remainder of query as regex content — count backticks per `expr`, must be even |

### Usage

```sh
# Static checks only (no cluster needed):
bash scripts/review-dashboard.sh path/to/dashboard.json

# With live Loki smoke test:
LOKI_URL=http://10.43.x.x:3100 bash scripts/review-dashboard.sh path/to/dashboard.json --live

# Or via SSH to an edge node (autodetects Loki ClusterIP):
EDGE_HOST=edge-dev bash scripts/review-dashboard.sh path/to/dashboard.json --live
```

### Backslash escaping reference

Three escaping layers interact in dashboard JSON:

| Layer | What `\\` means | Write `\` literal as |
|-------|----------------|---------------------|
| JSON string literal | one backslash | `\\` (two chars in source) |
| LogQL backtick raw string | two literal backslashes | n/a — raw, no escaping |
| Regex (RE2) | escape next char + identity → matches `\` | `\\\\` |

To match a **literal dot** in a LogQL backtick-regex (e.g. `pod.svc.cluster.local`):
- Inside backticks: `\.` (regex syntax)
- In JSON source: `\\.` (JSON-escapes the one backslash) → memory `\.` → LogQL receives raw `\.` → regex `\.` ✓

Common over-escape mistake: `\\\\.` in JSON (4 chars) → memory `\\.` → LogQL `\\.` → regex `\\.` (literal-backslash-then-any-char). Misses every actual dot.

### Common LogQL paren shapes

| Form | Trailing closes |
|------|-----------------|
| `count_over_time({...}[1h])` | `)` |
| `sum(count_over_time(...))` | `))` |
| `sum by (X) (count_over_time(...))` | `))` (the `(X)` is inline, balances itself) |
| `topk(N, sum by (X) (count_over_time(...)))` | `)))` |
| `count(count by (X) (count_over_time(...)))` | `)))` |

Inline parens in `by (X)` clauses are LogQL syntax (not function calls) and balance themselves on the same line — don't count them when checking trailing closes.

See [dashboard-review.md](references/dashboard-review.md) for the full checklist + script reference.
