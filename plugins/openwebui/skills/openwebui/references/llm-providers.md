# LLM Providers - Ollama, OpenAI, and Anthropic

## Ollama

Open WebUI is designed to be Protocol-Oriented. When referring to "Ollama", it means the Ollama API Protocol (typically running on port `11434`).

### Setting Up the Ollama Connection

Open WebUI automatically attempts to connect to your Ollama instance. If you encounter connection issues, refer to the connection troubleshooting guide.

### Managing Your Ollama Instance

1. Go to **Admin Settings** in Open WebUI.
2. Navigate to **Connections > Ollama > Manage** (click the wrench icon).

**Connection Tips:**
- **Docker Users**: Use `http://host.docker.internal:11434` as the URL.
- **Load Balancing**: Add multiple Ollama instances. Open WebUI distributes requests using random selection. Model IDs must match exactly across instances.

**Advanced Configuration:**
- **Prefix ID**: Use a prefix (e.g., `remote/`) to distinguish multiple instances serving the same model names.
- **Model IDs (Filter)**: Make specific models visible by listing them (whitelist). Leave empty to show all.
- **Connection Timeout**: `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=3` (default is 10 seconds)

### Download Models from Model Selector

Type the name of a model you want in the Model Selector. If it's not available, Open WebUI will prompt you to download it from Ollama.

### Using Reasoning / Thinking Models

For reasoning models like DeepSeek-R1 or Qwen3 that output thinking content in `<think>...</think>` tags, configure Ollama with a reasoning parser:

```bash
ollama serve --reasoning-parser deepseek_r1
```

The `deepseek_r1` parser works for most reasoning models including Qwen3.

## OpenAI

### Step 1: Get Your OpenAI API Key

- **OpenAI**: Get your key at [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- **Azure OpenAI**: Get your key from the [Azure Portal](https://portal.azure.com/)

### Step 2: Add the API Connection

1. Go to **Admin Settings**.
2. Navigate to **Connections > OpenAI > Manage** (wrench icon).
3. Click **Add New Connection**.

**OpenAI:**
- **Connection Type**: External
- **URL**: `https://api.openai.com/v1`
- **API Key**: Your secret key (starts with `sk-...`)

**Azure OpenAI:**
1. Find **Provider Type** and click to switch it to **Azure OpenAI**.
2. **URL**: Your Azure Endpoint (e.g., `https://my-resource.openai.azure.com`).
3. **API Version**: e.g., `2024-02-15-preview`.
4. **API Key**: Your Azure API Key.
5. **Model IDs (Deployments)**: You must add your specific Deployment Names.

**Advanced Configuration:**
- **Model IDs (Filter)**: Default (Empty) auto-detects all available models. Set to act as an allowlist.
- **Prefix ID**: Add a prefix (e.g., `groq/`) to distinguish models from multiple providers with the same name.
- **Connection Timeout**: `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=15` (default is 10 seconds)

### Step 3: Start Using Models

Select a model from the Model Selector and start chatting. No downloads needed for API-based models.

## Anthropic (Claude)

Open WebUI supports Anthropic's Claude models natively through their OpenAI-compatible endpoint. No middleware, no pipes, no extra setup required.

Open WebUI includes a built-in compatibility layer that automatically detects Anthropic URLs, handles model discovery, and translates requests. Chat completions, streaming, and tool calling all work out of the box.

Anthropic states that their OpenAI-compatible API is intended for evaluation and testing, not production workloads. For full Claude-native features (PDF processing, citations, extended thinking, prompt caching), use their native `/v1/messages` API via a pipe function or proxy like LiteLLM.

### Step 1: Get Your API Key

Go to [console.anthropic.com](https://console.anthropic.com/) and generate a new key.

### Step 2: Add the Connection

1. Go to **Admin Settings > Connections > OpenAI**.
2. Click **Add Connection**.
3. Enter:
   - **URL**: `https://api.anthropic.com/v1`
   - **API Key**: Your Anthropic API key
4. Click **Save**.

### Step 3: Start Chatting

Open WebUI automatically detects the Anthropic endpoint and fetches available models.

Common model IDs:
| Model | ID |
|---|---|
| Claude Opus 4.6 | `claude-opus-4-6` |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` |
| Claude Haiku 4.5 | `claude-haiku-4-5` |

You can enable or disable your Anthropic connection at any time using the toggle switch next to the connection entry.
