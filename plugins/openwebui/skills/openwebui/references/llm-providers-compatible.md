# LLM Providers - OpenAI-Compatible Services

Open WebUI connects to any server or provider that implements the OpenAI-compatible API.

## Protocol-Oriented Design

Open WebUI focuses on protocols like the OpenAI Chat Completions Protocol rather than building provider-specific modules. It also has experimental support for Open Responses.

## Connection Verification

When adding a connection, Open WebUI verifies by calling the provider's `/models` endpoint. Some providers do not implement this endpoint. The connection verification will fail but chat completions will still work. You just need to manually add model names to the Model IDs (Filter) allowlist.

| Provider | `/models` works? | Action Needed |
|---|---|---|
| Anthropic | Yes | Auto-detection works |
| GitHub Models | No | Add model IDs manually |
| Perplexity | No | Add model IDs manually |
| MiniMax | No | Add model IDs manually |
| OpenRouter | Yes (thousands of models) | Strongly recommend filtered allowlist |
| Google Gemini | Yes | Auto-detection works |
| DeepSeek | Yes | Auto-detection works |
| Mistral | Yes | Auto-detection works |
| Groq | Yes | Auto-detection works |

## Adding a Provider Connection

1. Go to **Admin Settings > Connections > OpenAI**.
2. Click **Add Connection**.
3. Fill in the **URL** and **API Key** (URL field suggests common provider endpoints).
4. If provider doesn't support `/models`, add model IDs to the **Model IDs (Filter)** allowlist.
5. Click **Save**.

If running Open WebUI in Docker with model server on host, replace `localhost` with `host.docker.internal`. Each connection has a toggle switch to enable/disable without deleting.

## Cloud Providers

| Provider | URL | API Key Source | Model IDs |
|---|---|---|---|
| Anthropic | `https://api.anthropic.com/v1` | console.anthropic.com | Auto-detected |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` (no trailing slash) | aistudio.google.com | Auto-detected |
| DeepSeek | `https://api.deepseek.com/v1` | platform.deepseek.com | Auto-detected |
| Mistral | `https://api.mistral.ai/v1` | console.mistral.ai | Auto-detected |
| Groq | `https://api.groq.com/openai/v1` | console.groq.com | Auto-detected |
| Perplexity | `https://api.perplexity.ai` | perplexity.ai/settings | Add manually (e.g., `sonar-pro`, `sonar-reasoning-pro`) |
| MiniMax | `https://api.minimax.io/v1` | Coding Plan API key | Add manually (e.g., `MiniMax-M2.5`) |
| OpenRouter | `https://openrouter.ai/api/v1` | openrouter.ai/keys | Strongly recommend filtered allowlist |

OpenRouter exposes thousands of models. Use an allowlist and enable model caching via `ENABLE_BASE_MODELS_CACHE=True`.

### Azure OpenAI

Switch the Provider Type button from OpenAI to Azure OpenAI:

| Setting | Value |
|---|---|
| **URL** | Your Azure endpoint (e.g., `https://my-resource.openai.azure.com`) |
| **API Version** | e.g., `2024-02-15-preview` |
| **API Key** | Your Azure API Key |
| **Model IDs** | Required -- add your Deployment Names |

Azure uses deployment names as model IDs, not standard OpenAI model names.

### LiteLLM

Proxy server providing unified OpenAI-compatible API across 100+ providers.

| Setting | Value |
|---|---|
| **URL** | `http://localhost:4000/v1` |
| **API Key** | Your LiteLLM proxy key (if configured) |

```bash
pip install litellm
litellm --model gpt-4 --port 4000
```

### Amazon Bedrock

Multiple OpenAI-compatible connection methods:
- **Bedrock Access Gateway (BAG)**: AWS proxy wrapping Bedrock SDK into OpenAI-compatible endpoints
- **stdapi.ai**: OpenAI-compatible API gateway deployed in your AWS account
- **LiteLLM**: With its Bedrock provider
- **Bedrock Mantle**: AWS native solution, no installation required

**Bedrock Mantle** (simplest):
```bash
OPENAI_API_BASE_URL=https://bedrock-mantle.us-east-1.api.aws/v1
OPENAI_API_KEY=your_bedrock_api_key
```

## Local Servers

| Server | URL | API Key |
|---|---|---|
| Llama.cpp | `http://localhost:10000/v1` | Leave blank |
| Lemonade | `http://localhost:8000/api/v1` | Leave blank |
| LM Studio | `http://localhost:1234/v1` | Leave blank or `lm-studio` |
| vLLM | `http://localhost:8000/v1` | Leave blank |
| LocalAI | `http://localhost:8080/v1` | Leave blank |
| Docker Model Runner | `http://localhost:12434/engines/llama.cpp/v1` | Leave blank |

## Required API Endpoints

| Endpoint | Method | Required? | Purpose |
|---|---|---|---|
| `/v1/models` | `GET` | Recommended | Model discovery. If not available, add models manually. |
| `/v1/chat/completions` | `POST` | **Yes** | Core chat endpoint with streaming support. |
| `/v1/embeddings` | `POST` | No | Required for RAG. |
| `/v1/audio/speech` | `POST` | No | Required for TTS. |
| `/v1/audio/transcriptions` | `POST` | No | Required for STT/Whisper. |
| `/v1/images/generations` | `POST` | No | Required for image generation. |

### Supported Parameters

Open WebUI passes: `temperature`, `top_p`, `max_tokens` (or `max_completion_tokens`), `stop`, `seed`, `logit_bias`. Also supports Tool Use (Function Calling) via `tools` and `tool_choice` parameters.

Connection timeout: `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST` (default 10 seconds).
