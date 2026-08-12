---
last_updated: 2026-03-08
---

# Distributed Tracing

## Core Concepts

### Trace
Complete request journey across services. Contains one or more spans sharing the same trace ID.

### Span
Single unit of work within a trace. Has name, start time, duration, parent span ID, attributes, events, and status.

```
Trace: abc123
+-- [200ms] HTTP GET /api/orders        (root span)
|   +-- [50ms]  auth.ValidateToken      (child span)
|   +-- [120ms] db.GetOrders            (child span)
|   |   +-- [80ms]  SQL SELECT          (grandchild)
|   |   +-- [30ms]  cache.Set           (grandchild)
|   +-- [20ms]  serialize.Response      (child span)
```

### Context Propagation
Passes trace context (trace ID, span ID) across process boundaries via HTTP headers (`traceparent`, `tracestate`) using W3C Trace Context format.

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
             ^  ^                                ^                ^
             |  trace-id                         span-id          sampled
             version
```

## Sampling Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `AlwaysSample` | Record every trace | Dev/testing, low-traffic services |
| `NeverSample` | Record nothing | Disable tracing |
| `TraceIDRatioBased(0.1)` | Sample 10% of traces | Production, high-traffic |
| `ParentBased(root)` | Follow parent's decision | Distributed systems (recommended) |

### Production Sampling Config

```go
// Sample 10% of traces, but always sample if parent was sampled
sampler := sdktrace.ParentBased(
    sdktrace.TraceIDRatioBased(0.1),
)

tp := sdktrace.NewTracerProvider(
    sdktrace.WithSampler(sampler),
)
```

### Tail-Based Sampling (Collector)

Sample decisions after seeing full trace -- keep errors and slow traces regardless of ratio:

```yaml
# OTEL Collector config — requires tail_sampling processor (contrib)
processors:
  tail_sampling:
    decision_wait: 10s       # Wait for full trace (default: 30s)
    num_traces: 50000        # Traces held in memory
    policies:
      - name: errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow-traces
        type: latency
        latency: {threshold_ms: 1000}
      - name: rate-limit
        type: rate_limiting
        rate_limiting: {spans_per_second: 100}
      - name: percentage
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

Note: All spans for a trace MUST arrive at the same collector instance. Use a load balancing exporter or trace-ID-aware routing in multi-collector setups.

See [tracing-patterns.md](tracing-patterns.md) for performance analysis patterns, N+1 detection, and span best practices.
