---
last_updated: 2026-03-08
---

# OTEL Collector: Processors, App Config, and Monitoring

## Key Processors

```yaml
processors:
  batch:                    # Batch for efficiency
    send_batch_size: 1024
    timeout: 5s

  memory_limiter:           # Prevent OOM
    check_interval: 1s
    limit_mib: 512

  attributes:               # Add/modify attributes
    actions:
      - key: environment
        value: production
        action: upsert

  filter:                   # Drop unwanted telemetry
    traces:
      span:
        - 'attributes["http.route"] == "/health"'

  tail_sampling:            # Keep errors + slow traces (requires contrib)
    decision_wait: 10s
    policies:
      - name: errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow
        type: latency
        latency: {threshold_ms: 1000}
      - name: rate-limit
        type: rate_limiting
        rate_limiting: {spans_per_second: 100}
      - name: sample
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

## Application Configuration

Apps send telemetry to the collector via environment variables:

```yaml
# In pod spec
env:
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector.observability.svc:4317"
  - name: OTEL_SERVICE_NAME
    value: "my-service"
  - name: OTEL_RESOURCE_ATTRIBUTES
    value: "deployment.environment=production,service.version=1.0.0"
```

## Health and Monitoring

```yaml
extensions:
  health_check:
    endpoint: 0.0.0.0:13133

service:
  extensions: [health_check]
  telemetry:
    metrics:
      address: 0.0.0.0:8888
```

Key collector self-metrics: `otelcol_receiver_accepted_spans`, `otelcol_exporter_sent_spans`, `otelcol_processor_dropped_spans`, `otelcol_exporter_queue_size`

## Troubleshooting

- **Spans not arriving**: Verify port 4317 accessible (NetworkPolicy)
- **High memory**: Add `memory_limiter` processor
- **Dropped spans**: Increase `sending_queue.queue_size` on exporter
- **Missing k8s attrs**: Enable `kubernetesAttributes` preset or add RBAC
- **CrashLoop**: Check `kubectl logs` for config validation errors
