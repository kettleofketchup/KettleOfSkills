# Model Context Protocol (MCP)

Open WebUI natively supports **MCP (Model Context Protocol)** starting in **v0.6.31**.

**Prerequisite**: You **MUST** set the `WEBUI_SECRET_KEY` environment variable. Without it, OAuth-connected MCP tools will break on container restart (`Error: Error decrypting tokens`).

## Quick Start

1. Open **Admin Settings > External Tools**
2. Click **+ (Add Server)**
3. Set **Type** to **MCP (Streamable HTTP)**
4. Enter **Server URL** and **Auth** details
5. **Save**

Make sure **Type** is set to **MCP (Streamable HTTP)**, not **OpenAPI**. Wrong type causes UI crash/infinite loading.

## When to Use MCP vs OpenAPI

**Choose OpenAPI** for: Enterprise readiness (SSO, API gateways, audit), operational resilience (HTTP verbs, idempotency, caching), observability.

**Choose MCP (Streamable HTTP)** for: Common tool protocol already used by your MCP servers/clients, streamed protocol communication over HTTP.

You can use both -- many teams expose OpenAPI internally and wrap MCP at the edge.

## Authentication Modes

- **None**: For local MCP servers or internal networks. Default to this unless server requires a token. Selecting "Bearer" without a key sends empty Authorization header, causing rejection.
- **Bearer**: Only if server requires a specific API token. Must populate "Key" field.
- **OAuth 2.1**: Uses Dynamic Client Registration (DCR).
- **OAuth 2.1 (Static)**: Uses pre-created client ID/client secret. For providers that don't support DCR.

### OAuth 2.1 (Static) Setup

1. Admin Settings > External Tools > + Add Server
2. Type: MCP (Streamable HTTP)
3. Enter URL
4. Auth: OAuth 2.1 (Static)
5. Enter Client ID and Client Secret
6. Click Register Client > Save

Then in chat: + > Integrations > Tools > Enable MCP tool > Complete OAuth flow.

**OAuth 2.1 tools cannot be set as default tools** on a model. The auth flow requires interactive browser redirect. Users must manually enable per-chat via + button.

## Connection URLs

In Docker with MCP server on host machine: use `http://host.docker.internal:<port>` instead of `localhost`.

## Function Name Filter List

Leave empty to expose all tools. If connection errors with empty list, try adding a single comma (`,`).

## Troubleshooting

### "Failed to connect to MCP server"

1. Check authentication -- switch to `None` if no token needed
2. Function Name Filter List -- try adding comma (`,`)
3. OAuth 2.1 default tool limitation -- remove from model defaults, have users enable manually

### Infinite loading screen

Cause: MCP server configured as OpenAPI type.
Fix: Disable problematic connection in Admin Settings, refresh, re-add with correct MCP type.

## FAQ

**Supported transports?** Streamable HTTP only. For stdio/SSE, use [mcpo](https://github.com/open-webui/mcpo) as proxy.

**Is MCP stable?** Supported and improving. Broader ecosystem still evolving.

**Can I mix OpenAPI and MCP?** Yes. Many deployments do both.
