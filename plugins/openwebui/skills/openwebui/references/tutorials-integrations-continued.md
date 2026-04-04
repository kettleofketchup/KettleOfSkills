# Integration Tutorials (Continued)

## OneDrive Personal Integration (Optional)

To enable support for personal Microsoft accounts, create a **second, separate App Registration** configured for consumers.

### Step 1: Create a Separate App Registration for Personal Accounts

1. Navigate back to **App registrations** and select **+ New registration**.
2. Name it distinctly (e.g., "Open WebUI Personal Integration").
3. Under "Supported account types," select: **"Accounts in any organizational directory (Multitenant) and personal Microsoft accounts (e.g., Skype, Xbox)"**.
4. Configure the **SPA Redirect URI** with your Open WebUI base URL.
5. **Enable both "Access tokens" and "ID tokens"** under "Implicit grant and hybrid flows".
6. No special API permissions or admin consent are required -- users will consent to `OneDrive.ReadWrite` individually.

### Step 2: Configure the Environment Variable

```bash
# Personal Account Configuration (Optional)
ONEDRIVE_CLIENT_ID_PERSONAL="zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"
```

### Final Step: Enable OneDrive Integration in Admin Settings

After setting environment variables and restarting, enable the feature in the admin panel. **The environment variables alone do not activate the integration.**

1. Navigate to **Settings > Admin > Documents**.
2. Toggle on the **"OneDrive"** switch.
3. Refresh your browser or log out and log back in.

The admin toggle is mandatory even though you've set `ENABLE_ONEDRIVE_INTEGRATION=true`. Some configuration options are persistent database settings initialized on first startup but must be activated through the admin interface.

### Verifying the Integration

1. In Open WebUI, open the attachment menu (+) in the chat input.
2. You should see **"Microsoft OneDrive (work/school)"** and/or **"Microsoft OneDrive (personal)"**.
3. Clicking either option should trigger a pop-up window for Microsoft authentication.

**Note:** The OneDrive file picker and authentication flow happen in a pop-up window. You must disable the pop-up blocker for your Open WebUI domain.

### Troubleshooting

- **OneDrive option not appearing**: Verify the admin toggle is enabled, refresh browser, check environment variables and container restart.
- **Files not loading**: Log out and back in to refresh tokens, verify Azure permissions and admin consent.
- **Authentication pop-up not appearing**: Disable pop-up blockers, try Edge browser.

---

## DeepSeek R1 Dynamic (Full 671B via Llama.cpp)

Run the **full DeepSeek-R1** 671B parameter model in its dynamic 1.58-bit quantized form (compressed to 131GB) on **Llama.cpp**.

**Note:** The only true **DeepSeek-R1** model on Ollama is the **671B version** at `ollama.com/library/deepseek-r1:671b`. Other versions are **distilled** models.

### Step 1: Install Llama.cpp

Download prebuilt binaries from the GitHub releases page, or build from source following the Llama.cpp Build Guide.

### Step 2: Download the Model

Download from Unsloth's Hugging Face page (`unsloth/DeepSeek-R1-GGUF`):

```python
# pip install huggingface_hub hf_transfer
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id = "unsloth/DeepSeek-R1-GGUF",
    local_dir = "DeepSeek-R1-GGUF",
    allow_patterns = ["*UD-IQ1_S*"],  # 1.58-bit version
)
```

### Step 3: Serve the Model Using Llama.cpp

```bash
./llama-server \
    --model /path/to/DeepSeek-R1-GGUF/DeepSeek-R1-UD-IQ1_S/DeepSeek-R1-UD-IQ1_S-00001-of-00003.gguf \
    --port 10000 \
    --ctx-size 1024 \
    --n-gpu-layers 40
```

Key parameters:
- **`--model`:** Path to the GGUF files.
- **`--port`:** Server port (default `8080`).
- **`--ctx-size`:** Context length in tokens. Increase if hardware allows.
- **`--n-gpu-layers`:** Number of layers offloaded to GPU for faster inference.

The server hosts a **local OpenAI-compatible API** at `http://127.0.0.1:10000`.

### Step 4: Connect Llama.cpp to Open WebUI

1. Go to **Admin Settings** in Open WebUI.
2. Navigate to **Connections > OpenAI Connections**.
3. Add:
   - URL: `http://127.0.0.1:10000/v1` (or `http://host.docker.internal:10000/v1` when running Open WebUI in Docker)
   - API Key: `none`

### Notes

- **Performance:** Running a 131GB model on personal hardware will be **slow**. Even with M4 Max (128GB RAM), inference speeds are modest.
- **VRAM/Memory:** Ensure sufficient VRAM and system RAM. CPU-only setups will be slower but still functional.
