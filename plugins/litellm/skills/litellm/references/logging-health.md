# Logging & Health Checks

## Logging Configuration

```yaml
litellm_settings:
  success_callback: ["langfuse", "s3_v2"]
  failure_callback: ["sentry"]
  callbacks: ["otel"]                        # Both success + failure
```

## Supported Backends (20+)

Langfuse, OpenTelemetry, S3, GCS, Datadog, Sentry, Langsmith, Lunary, DynamoDB, Azure Blob Storage, Arize AI, custom webhooks, custom Python callbacks, and more.

## Privacy Controls

```yaml
litellm_settings:
  turn_off_message_logging: true            # No request/response content logged
  redact_user_api_key_info: true            # Redact key info from logs
```

Per-key: `"metadata": {"mask_input": true, "mask_output": true}`
Per-request: `"no-log": true` in metadata to skip logging entirely.

## Health Endpoints

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `/health` | Yes | Full model health (real API calls) |
| `/health/readiness` | No | DB connectivity |
| `/health/liveliness` | No | Alive check |
| `/health/services` | Yes | Integration health (langfuse, datadog) |

## Background Health Checks

```yaml
general_settings:
  background_health_checks: true
  health_check_interval: 300               # Seconds
```

## Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/liveliness
    port: 4000
  initialDelaySeconds: 120
readinessProbe:
  httpGet:
    path: /health/readiness
    port: 4000
  initialDelaySeconds: 120
```
