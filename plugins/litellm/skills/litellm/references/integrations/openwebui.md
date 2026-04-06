# Open WebUI Integration

LiteLLM exposes an OpenAI-compatible API at `/v1`, making it a drop-in backend for Open WebUI.

## Configuration

### Open WebUI Environment Variables

```
OPENAI_API_BASE_URL=http://litellm:4000/v1
OPENAI_API_KEY=sk-your-litellm-key
```

### Docker Compose Example

```yaml
services:
  litellm:
    image: docker.litellm.ai/berriai/litellm:main-stable
    command: --config /app/config.yaml
    volumes:
      - ./config.yaml:/app/config.yaml
    env_file: .env
    ports:
      - "4000:4000"

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      OPENAI_API_BASE_URL: http://litellm:4000/v1
      OPENAI_API_KEY: sk-your-litellm-key
    ports:
      - "3000:8080"
    depends_on:
      - litellm
```

### Kubernetes

In Open WebUI Helm values, set the OpenAI-compatible connection:

```yaml
# open-webui values.yaml
env:
  - name: OPENAI_API_BASE_URL
    value: "http://litellm.litellm-ns.svc.cluster.local:4000/v1"
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: litellm-key
        key: api-key
```

## How It Works

1. All models in LiteLLM's `model_list` appear in Open WebUI's model selector via `/v1/models`
2. Open WebUI sends requests to LiteLLM's `/v1/chat/completions` endpoint
3. LiteLLM routes to the correct provider (OpenAI, Anthropic, vLLM, etc.)
4. Spend tracking, rate limiting, and logging apply transparently

## Per-User Keys

For per-user spend tracking, generate individual LiteLLM virtual keys and configure each Open WebUI user with their own key. Or use JWT auth with Open WebUI's OIDC integration to pass through user identity.

## Model Filtering

Restrict which models appear in Open WebUI by scoping the virtual key:

```bash
curl -X POST 'http://litellm:4000/key/generate' \
  -H 'Authorization: Bearer sk-master-key' \
  -d '{"models": ["gpt-4", "claude-3-opus"], "max_budget": 50}'
```

Only `gpt-4` and `claude-3-opus` will appear in Open WebUI when using this key.
