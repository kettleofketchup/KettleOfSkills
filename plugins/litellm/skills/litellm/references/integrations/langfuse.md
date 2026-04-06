# Langfuse Integration

LiteLLM sends traces, costs, and metadata to Langfuse for LLM observability.

## Setup

```yaml
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]
  langfuse_default_tags:
    - "cache_hit"
    - "user_api_key_alias"
    - "user_api_key_team_alias"
```

Environment variables:
```
LANGFUSE_PUBLIC_KEY="pk_xxx"
LANGFUSE_SECRET_KEY="sk_xxx"
LANGFUSE_HOST="https://langfuse.example.com"   # Self-hosted only
```

## Metadata Passing

### Via Request Body

```json
{
  "metadata": {
    "generation_name": "test-generation",
    "trace_id": "trace-123",
    "session_id": "sess-1",
    "tags": ["tag1", "tag2"]
  }
}
```

### Via Headers (Proxy)

```
langfuse_trace_id: trace-id-2
langfuse_trace_user_id: user-id-2
langfuse_trace_metadata: {"key": "value"}
```

## Trace Features

- **Custom trace IDs**: Set `trace_id` in metadata for correlation
- **Session grouping**: Set `session_id` to group related traces
- **Trace continuation**: Use `existing_trace_id` to append to existing trace
- **Per-request credentials**: Send different Langfuse keys per request (multi-project)

## Redaction & Privacy

```json
{
  "metadata": {
    "mask_input": true,
    "mask_output": true
  }
}
```

Global: `turn_off_message_logging: true` in litellm_settings.
Per-request: `"no-log": true` in metadata skips logging entirely.

## Verify Integration

Check health: `GET /health/services?service=langfuse` (requires auth).
