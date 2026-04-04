# Open WebUI Monitoring & OpenTelemetry

## Health Check Levels

### Level 1: Basic Health Check
`GET /health` -- No auth required, returns 200 when service is up. Verifies web server, app initialization, basic DB connectivity.

**Uptime Kuma:** HTTP(s) monitor, URL: `http://instance:8080/health`, interval 60s, retries 3.

### Level 2: Model Connectivity
`GET /api/models` -- Requires auth. Confirms model provider connections.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://instance:8080/api/models
```

**Uptime Kuma:** HTTP(s) JSON Query, header `Authorization: Bearer KEY`, query `$count(data[*])>0`, expected `true`, interval 300s.

**Advanced JSONata queries:**
- Ollama models: `$count(data[owned_by='ollama'])>0`
- Specific model: `$exists(data[id='gpt-4o'])`
- Multiple models: `$count(data[id in ['gpt-4o', 'gpt-4o-mini']]) = 2`

Use a dedicated non-admin monitoring account for API keys.

### Level 3: Deep Health Check (End-to-End)
`POST /api/chat/completions` -- Send real prompt, validate response.

```bash
curl -X POST http://instance:8080/api/chat/completions \
  -H "Authorization: Bearer KEY" -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Respond with the word HEALTHY"}], "model": "llama3.1", "temperature": 0}'
```

Catches model loading failures, backend processing errors, provider-side issues.

## OpenTelemetry Integration

### Quick Start
```bash
docker compose -f docker-compose.otel.yaml up -d
```
Sets up Grafana LGTM (Loki+Grafana+Tempo+Mimir) on port 3000, Open WebUI on port 8088.

Grafana login: `admin` / `admin`.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ENABLE_OTEL` | `false` | Master switch for OpenTelemetry |
| `ENABLE_OTEL_TRACES` | `false` | Enable distributed tracing |
| `ENABLE_OTEL_METRICS` | `false` | Enable FastAPI HTTP metrics |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | - | OTLP collector endpoint (e.g., `http://grafana:4317`) |
| `OTEL_EXPORTER_OTLP_INSECURE` | `false` | Skip TLS for OTLP |
| `OTEL_SERVICE_NAME` | `open-webui` | Service name in traces/metrics |
| `OTEL_METRICS_EXPORT_INTERVAL_MILLIS` | `10000` | Metrics export interval (ms) |
| `OTEL_BASIC_AUTH_USERNAME` | - | Basic auth for collector |
| `OTEL_BASIC_AUTH_PASSWORD` | - | Basic auth for collector |

### Distributed Tracing

Auto-instrumented: FastAPI routes, SQLAlchemy queries, Redis, requests/httpx/aiohttp calls.

Span data includes: `db.instance`, `db.statement`, `redis.args`, `http.url`, `http.method`, `http.status_code`, error details.

### Metrics

| Instrument | Type | Unit | Labels |
|---|---|---|---|
| `http.server.requests` | Counter | 1 | `http.method`, `http.route`, `http.status_code` |
| `http.server.duration` | Histogram | ms | (same) |

### Custom Collector Setup
```bash
docker run -d --name open-webui -p 8088:8080 \
  -e ENABLE_OTEL=true -e ENABLE_OTEL_TRACES=true -e ENABLE_OTEL_METRICS=true \
  -e OTEL_EXPORTER_OTLP_ENDPOINT=http://your-collector:4317 \
  -e OTEL_EXPORTER_OTLP_INSECURE=true -e OTEL_SERVICE_NAME=open-webui \
  -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main
```

### Troubleshooting OTel

- Verify `ENABLE_OTEL`, `ENABLE_OTEL_TRACES`, `ENABLE_OTEL_METRICS` are all `true`
- Check `OTEL_EXPORTER_OTLP_ENDPOINT` is correct
- Check Open WebUI logs for OTLP errors
- Verify collector port 4317 is reachable: `curl http://localhost:4317`
- For auth-protected collectors: set `OTEL_BASIC_AUTH_USERNAME`/`PASSWORD`
- For SSL/TLS: adjust `OTEL_EXPORTER_OTLP_INSECURE`

If running from source/pip (not Docker), install dependencies manually:
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```
