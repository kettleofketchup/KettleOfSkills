# LLM Configuration

OpenHands routes all providers through LiteLLM, so model strings follow LiteLLM naming:
`<provider>/<model>`.

## Direct Providers

```bash
# Anthropic
LLM_MODEL=anthropic/claude-sonnet-4-5-20250929
LLM_API_KEY=sk-ant-...

# OpenAI
LLM_MODEL=openai/gpt-5.2
LLM_API_KEY=sk-...

# Google
LLM_MODEL=gemini/gemini-2.5-pro
LLM_API_KEY=...

# Azure
LLM_MODEL=azure/<deployment-name>
LLM_BASE_URL=https://<resource>.openai.azure.com
LLM_API_KEY=...
LLM_API_VERSION=2024-10-21

# Bedrock
LLM_MODEL=bedrock/anthropic.claude-sonnet-4-5-v1:0
LLM_AWS_ACCESS_KEY_ID=...
LLM_AWS_SECRET_ACCESS_KEY=...
LLM_AWS_REGION_NAME=us-east-1

# OpenRouter
LLM_MODEL=openrouter/anthropic/claude-sonnet-4.5
LLM_API_KEY=sk-or-...
```

Confirm current model IDs against the provider — model names change faster than docs.

## LiteLLM Gateway (Recommended for Teams)

Point every OpenHands instance at one gateway instead of distributing provider keys.

```bash
LLM_MODEL=litellm_proxy/claude-sonnet-4-5     # name as defined in the gateway's model_list
LLM_BASE_URL=http://litellm.litellm.svc.cluster.local:4000
LLM_API_KEY=sk-<virtual-key>
```

In the UI: enable **Advanced** options, then set Custom Model `litellm_proxy/<name>`, Base URL, and API Key.

The `litellm_proxy/` prefix is required. Without it LiteLLM tries to resolve the name against real providers
and returns a model-not-found error that looks like a gateway problem.

Why this is the right default for multi-user:

- Per-user virtual keys with hard budget caps
- Spend attribution per user/team
- Model swaps without touching OpenHands
- Fallbacks and rate limiting centrally
- Provider keys never reach a sandbox the user controls

See the `litellm` skill for gateway configuration.

## Local Models

```bash
# Ollama
LLM_MODEL=ollama/qwen3-coder:30b
LLM_BASE_URL=http://host.docker.internal:11434
LLM_API_KEY=ollama              # ignored but must be non-empty

# vLLM / any OpenAI-compatible server
LLM_MODEL=openai/Qwen/Qwen3-Coder-30B
LLM_BASE_URL=http://vllm:8000/v1
LLM_API_KEY=dummy
```

From a container, `localhost` is the container. Use `host.docker.internal` (with
`--add-host host.docker.internal:host-gateway`) or the service DNS name.

Agent work needs long contexts and reliable tool calling. Small local models frequently fail the tool-calling
loop rather than the coding — if the agent thrashes, test tool calling before blaming the model's coding
ability. Set `LLM_INPUT_COST_PER_TOKEN=0` / `LLM_OUTPUT_COST_PER_TOKEN=0` so budget tracking doesn't misreport.

## Tuning

| Variable | Guidance |
|----------|----------|
| `LLM_CACHING_PROMPT=true` | Default on; large saving on long agent loops |
| `LLM_TEMPERATURE=0.0` | Default; raise only when exploring |
| `LLM_REASONING_EFFORT` | `high` for hard tasks on reasoning models |
| `LLM_NUM_RETRIES=8` | Lower for fast failure in CI |
| `LLM_DROP_PARAMS=true` | Needed for providers rejecting unsupported params |
| `LLM_DISABLE_VISION=true` | Cuts cost when screenshots aren't needed |
| `LLM_MAX_INPUT_TOKENS` | Cap context to bound per-step cost |

## Budgets

`MAX_BUDGET_PER_TASK` (default `0.0` = unlimited) and `MAX_ITERATIONS` (default `100`) are the agent's only
stop conditions — it cannot tell when it's stuck. Enforce the real ceiling at the LiteLLM virtual key as well:
env vars are per-instance and a user can raise them in the Settings UI.

## Custom LLM Profiles

Named configurations let different components use different models — e.g. a strong model for the agent and a
cheap one for condensing history. Configure them under Settings → LLM Profiles, or reference a named group
with `AGENT_LLM_CONFIG`. The SDK equivalent is the LLM registry / profile store
(→ `sdk.md`).

## Verifying

```bash
docker logs -f openhands-app | grep -i llm
```

| Symptom | Cause |
|---------|-------|
| `model not found` via gateway | Missing `litellm_proxy/` prefix, or name absent from `model_list` |
| 401 from gateway | Virtual key revoked or budget exhausted |
| Agent loops without acting | Model can't tool-call reliably — switch models |
| Truncated/failed long tasks | `LLM_MAX_INPUT_TOKENS` too low, or context exceeded |
| Costs far above expectation | `LLM_CACHING_PROMPT` disabled, or no `MAX_ITERATIONS` |
