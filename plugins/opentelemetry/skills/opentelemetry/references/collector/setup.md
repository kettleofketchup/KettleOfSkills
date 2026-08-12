---
last_updated: 2026-03-08
---

# OTEL Collector on Kubernetes

## Overview

The OpenTelemetry Collector receives, processes, and exports telemetry data. Decouples apps from specific backends.

```
Apps -> Collector (DaemonSet/Deployment) -> Backends
         receivers -> processors -> exporters
```

## Deployment Modes

| Mode | K8s Resource | Use Case |
|------|-------------|----------|
| **DaemonSet** | One per node | Low latency, node-level collection |
| **Deployment** | Centralized | Aggregation, tail sampling |
| **Sidecar** | Per pod | Isolation, per-app config |
| **Gateway** | Deployment + HPA | Multi-cluster, load-balanced ingestion |

Recommended: DaemonSet (fast local ingestion) -> Gateway (sampling, enrichment) -> Backends

## Helm Installation

```bash
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts

helm install otel-collector open-telemetry/opentelemetry-collector \
    --namespace observability --create-namespace \
    -f collector-values.yaml
```

### DaemonSet Values

```yaml
# collector-values.yaml
mode: daemonset

presets:
  kubernetesAttributes:
    enabled: true    # Adds k8s.pod.name, k8s.namespace.name, etc.

config:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

  processors:
    batch:
      send_batch_size: 1024
      timeout: 5s
    memory_limiter:
      check_interval: 1s
      limit_mib: 512
      spike_limit_mib: 128
    k8sattributes:
      extract:
        metadata:
          - k8s.pod.name
          - k8s.namespace.name
          - k8s.deployment.name
          - k8s.node.name
      pod_association:
        - sources:
            - from: resource_attribute
              name: k8s.pod.ip

  exporters:
    otlp/tempo:
      endpoint: tempo-distributor.observability.svc:4317
      tls:
        insecure: true
    otlp/jaeger:
      endpoint: jaeger-collector.observability.svc:4317
      tls:
        insecure: true
    prometheusremotewrite:
      endpoint: http://prometheus.observability.svc:9090/api/v1/write
    # Loki v3+ supports native OTLP — use otlphttp instead of deprecated loki exporter
    otlphttp/loki:
      endpoint: http://loki.observability.svc:3100/otlp

  service:
    pipelines:
      traces:
        receivers: [otlp]
        processors: [memory_limiter, k8sattributes, batch]
        exporters: [otlp/tempo]
      metrics:
        receivers: [otlp]
        processors: [memory_limiter, batch]
        exporters: [prometheusremotewrite]
      logs:
        receivers: [otlp]
        processors: [memory_limiter, k8sattributes, batch]
        exporters: [otlphttp/loki]

ports:
  otlp:
    enabled: true
    containerPort: 4317
    servicePort: 4317
    protocol: TCP
  otlp-http:
    enabled: true
    containerPort: 4318
    servicePort: 4318
    protocol: TCP

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

See [collector-advanced.md](collector-advanced.md) for processor configs, application env vars, health monitoring, and troubleshooting.
