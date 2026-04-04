# Integration Tutorials

**Connect Open WebUI to LLM providers, developer tools, monitoring platforms, and external services.**

### LLM Providers

| Tutorial | What you'll achieve | Details |
|----------|-------------------|---------|
| Azure OpenAI (Entra ID) | Keyless authentication to Azure OpenAI via Entra ID | Admin, 30-60 min |
| DeepSeek R1 Dynamic | Run the full 671B DeepSeek-R1 model via llama.cpp | Developer, 45 min |
| Intel GPU (IPEX-LLM) | Accelerate Ollama with IPEX-LLM on Intel GPUs | Developer, 20 min |

### Monitoring & Observability

| Tutorial | What you'll achieve | Details |
|----------|-------------------|---------|
| Helicone | Log and monitor LLM API calls, costs, and latency | Admin, 15 min |
| Langfuse | Trace LLM usage and evaluate prompt quality | Admin, 20 min |

### Developer Tools

| Tutorial | What you'll achieve | Details |
|----------|-------------------|---------|
| Continue.dev | Use Open WebUI as a backend for the Continue VS Code extension | Developer, 15 min |
| Jupyter Notebooks | Run code and create notebooks via Open WebUI's code interpreter | Developer, 20 min |
| iTerm2 | Query Open WebUI models from your macOS terminal | Developer, 10 min |
| Firefox Sidebar | Pin Open WebUI in Firefox's built-in AI sidebar | User, 5 min |
| Browser Search Engine | Add Open WebUI as a custom browser search engine | User, 5 min |

### External Services

| Tutorial | What you'll achieve | Details |
|----------|-------------------|---------|
| Notion (MCP) | Connect Notion as a knowledge source via Model Context Protocol | User, 20 min |
| OneDrive & SharePoint | Pull Microsoft 365 documents into Open WebUI | Admin, 30 min |
| LibreTranslate | Add self-hosted translation capabilities | Admin, 15 min |

---

## OneDrive & SharePoint Integration

### Prerequisites

- An active Microsoft Azure account with administrative privileges to create and manage App Registrations.
- Access to your Open WebUI instance's environment variables.

### Business & SharePoint (Work/School)

**Step 1: Create the Azure App Registration**

1. Navigate to the Microsoft Entra ID admin center.
2. Go to **Identity > Applications > App registrations**.
3. Select **+ New registration**.
4. Name the application (e.g., "Open WebUI Business Integration").
5. Under "Supported account types," select **"Accounts in this organizational directory only (Single tenant)"** or **"Accounts in any organizational directory (Multitenant)"**.
6. Leave "Redirect URI" blank. Click **Register**.

**Step 2: Configure the SPA Redirect URI**

1. From the App Registration overview, go to **Authentication**.
2. Click **+ Add a platform** and select **Single-page application (SPA)**.
3. Under "Redirect URIs", enter your Open WebUI base URL (e.g., `https://open-webui.yourdomain.com`).
4. **Enable both "Access tokens" and "ID tokens"** under "Implicit grant and hybrid flows".
5. Click **Configure**.

**Step 3: Configure API Permissions**

1. Go to **API permissions** tab.
2. Click **+ Add a permission** and select **Microsoft Graph**.
3. Select **Delegated permissions**.
4. Add: `Files.Read`, `Files.Read.All`, `Sites.Read.All`, `User.Read`, `AllSites.Read`, `MyFiles.Read`, `Sites.Search.All`.
5. If your organization uses SharePoint API permissions separately, repeat for **SharePoint**.
6. Click **"Grant admin consent for [Your Tenant Name]"**.

**Admin Consent is Mandatory.** Open WebUI uses the `.default` scope. If admin consent is not granted, non-admin users will be blocked with an "Admin approval required" error.

**Step 4: Gather Credentials**

From the **Overview** page, copy:
- **Application (client) ID** -> `ONEDRIVE_CLIENT_ID_BUSINESS`
- **Directory (tenant) ID** -> `ONEDRIVE_SHAREPOINT_TENANT_ID`

**Step 5: Configure Environment Variables**

```bash
# Enable the OneDrive integration feature globally
ENABLE_ONEDRIVE_INTEGRATION=true

# Business & SharePoint Configuration
ONEDRIVE_CLIENT_ID_BUSINESS="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
ONEDRIVE_SHAREPOINT_TENANT_ID="yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
ONEDRIVE_SHAREPOINT_URL="https://your-tenant-name.sharepoint.com"
```
