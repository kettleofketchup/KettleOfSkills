# Reliability & Caching

## Fallbacks

```yaml
litellm_settings:
  fallbacks: [{"gpt-3.5-turbo": ["gpt-4", "claude-3-haiku"]}]
  context_window_fallbacks: [{"claude-2": ["claude-3-opus"]}]
  content_policy_fallbacks: [{"claude-2": ["fallback-model"]}]
  default_fallbacks: ["claude-opus"]       # Catch-all fallback
  allowed_fails: 3                          # Failures before cooldown
  cooldown_time: 30                         # Seconds in cooldown
  enable_pre_call_checks: true              # Check context window before calling
```

## Retries & Timeouts

```yaml
litellm_settings:
  num_retries: 3
  request_timeout: 60        # Seconds

router_settings:
  num_retries: 3
  timeout: 30
```

## Routing Strategies

| Strategy | Behavior |
|----------|----------|
| `simple-shuffle` | Random distribution (default) |
| `least-busy` | Route to deployment with fewest active requests |
| `usage-based-routing` | Balance by TPM/RPM usage |
| `latency-based-routing` | Route to lowest latency deployment |

```yaml
router_settings:
  routing_strategy: "usage-based-routing"
```

## Caching

Supported backends: Redis, local (in-memory), disk, S3, GCS, Redis Semantic, Qdrant Semantic.

```yaml
litellm_settings:
  cache: true
  cache_params:
    type: redis                  # or local, disk, s3, gcs, qdrant-semantic, redis-semantic
    ttl: 600
    namespace: "litellm.caching"
    supported_call_types: ["acompletion", "aembedding"]
```

### Per-Request Cache Control

```json
{"cache": {"ttl": 300}}    // Custom TTL
{"no-cache": true}          // Bypass cache, store result
{"no-store": true}          // Bypass cache, don't store
```
