# LLM Providers - vLLM, Llama.cpp, Open Responses, Functions

## vLLM

vLLM provides an OpenAI-compatible API (Chat Completions).

### Step 1: Set Up Your vLLM Server

Default API base URL: `http://localhost:8000/v1`

### Step 2: Add the API Connection in Open WebUI

1. Go to **Admin Settings**.
2. Navigate to **Connections > OpenAI > Manage**.
3. Click **Add New Connection**.
4. Fill in:
   - **API URL**: `http://localhost:8000/v1` (or your vLLM server URL)
   - Docker users: Use `http://host.docker.internal:8000/v1`
   - **API Key**: `none` (or leave empty)
5. Click **Save**.

Connection timeout: `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=30` for slower model initialization.

## Llama.cpp

### Step 1: Install Llama.cpp

- [Download prebuilt binaries](https://github.com/ggerganov/llama.cpp/releases)
- Or [build from source](https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md)

### Step 2: Download a Supported Model

Download GGUF-format quantized LLMs. Example with Python:

```python
# pip install huggingface_hub hf_transfer
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id = "unsloth/DeepSeek-R1-GGUF",
    local_dir = "DeepSeek-R1-GGUF",
    allow_patterns = ["*UD-IQ1_S*"],
)
```

### Step 3: Serve the Model

```bash
./llama-server \
  --model /your/full/path/to/model.gguf \
  --port 10000 \
  --ctx-size 1024 \
  --n-gpu-layers 40
```

Parameters:
- `--model`: Path to your .gguf model file
- `--port`: 10000 (or another open port)
- `--ctx-size`: Token context length
- `--n-gpu-layers`: Layers offloaded to GPU

### Step 4: Connect to Open WebUI

1. Go to **Admin Settings > Connections > OpenAI**.
2. Click **Add Connection**.
3. Set:
   - **URL**: `http://127.0.0.1:10000/v1`
   - Docker: Use `http://host.docker.internal:10000/v1` (note the `/v1`)
   - **API Key**: `none` (leave blank)

Connection timeout: `AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST=30`

## Open Responses

Experimental support for the [Open Responses](https://www.openresponses.org/) specification for multi-provider, interoperable LLM interfaces.

Open Responses standardizes how LLM requests and responses are structured across providers:
- One spec, many providers
- Composable agentic loops with unified streaming and tool invocation
- Easier evaluation and routing

### Configuration

1. Go to **Admin Settings > Connections > OpenAI > Manage**.
2. Add or edit a connection.
3. In the connection modal, find **API Type** and switch to **Responses** (experimental).
4. Enter the connection details for a provider that supports Open Responses.

### Stateful Sessions

By default, Open WebUI treats Responses API connections as stateless. To enable stateful sessions (server-side response storage with `previous_response_id`), set `ENABLE_RESPONSES_API_STATEFUL=true`. Only use this with providers that explicitly support it.

## Pipe Functions

Pipe Functions are "bring-your-own-model (or tool)" plugins:
- Act like models in the UI sidebar
- Integrate with any backend, API, or workflow -- no OpenAI compatibility required
- No LLM required -- build plugins for search, home automation, weather, databases, etc.
- Pure Python code running inside Open WebUI

### Setting Up a Pipe Function

1. Browse [Open WebUI Community Search](https://openwebui.com/search) (community account required).
2. Find a function (e.g., [Anthropic Pipe](https://openwebui.com/f/justinrahb/anthropic)).
3. Click **Get**, enter your Open WebUI URL, click **Import to Open WebUI**.
4. Review the Python code for safety and click **Save**.
5. Enable the function with the toggle switch.
6. Configure **Valves** (gear icon) with required API keys.
7. Select the new function as a model in the chat interface.

### Security Notes

- Always review function code before enabling.
- Only use plugins from trusted sources.
- Functions run arbitrary Python inside your WebUI instance.
