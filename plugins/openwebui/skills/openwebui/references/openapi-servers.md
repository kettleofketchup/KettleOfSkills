# OpenAPI Tool Servers

Reference OpenAPI Tool Server implementations for integrating external tooling and data sources into LLM agents and workflows.

## Why OpenAPI?

- **Established Standard**: Widely used, production-proven API standard.
- **No Reinventing the Wheel**: If you build REST APIs or use OpenAPI, you're already set.
- **Easy Integration & Hosting**: Deploy externally or locally without vendor lock-in.
- **Strong Security**: Supports HTTPS, OAuth, JWT, API Keys.

## Limitations

- **One-way events only**: Can emit status updates, notifications via REST endpoint. Interactive events (user input, confirmations) only available for native Python tools.
- **No streaming output**: Responses are complete results, not streamed.

## Quickstart

```bash
git clone https://github.com/open-webui/openapi-servers
cd openapi-servers/servers/filesystem
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --reload
```

With Docker:
```bash
docker compose up
```

## Open WebUI Integration

### Step 1: Launch an OpenAPI Tool Server

```bash
cd openapi-servers/servers/time
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --reload
```

### Step 2: Connect in Open WebUI

1. Open Settings > Tools > + (Add)
2. Enter URL (e.g., `http://localhost:8000`)
3. Save

### User Tool Servers vs Global Tool Servers

| Type | Request Origin | Localhost? | Use Case |
|------|---------------|-----------|----------|
| User Tool Server | Browser (Client-side) | Yes (private) | Personal tools, local dev/testing |
| Global Tool Server | Backend (Server-side) | No (unless on backend) | Team/shared tools, enterprise |

**User Tool Servers**: Requests from your browser. Can connect to localhost. Only your browser can access.
**Global Tool Servers**: Requests from Open WebUI backend. `localhost` means the backend server, not your machine.

### Using mcpo Config File

Each tool mounted under unique path:
- `http://localhost:8000/time`
- `http://localhost:8000/memory`

Enter full route per tool, NOT just root URL.

### Step 3: Confirm Connection

Tool server indicator appears in message input area. Click to view connected tools.

Global tools are hidden by default -- enable via + button in chat input area.

## MCP-to-OpenAPI Proxy (mcpo)

The mcpo proxy lets you use MCP servers via standard REST/OpenAPI APIs.

If connecting with API Key or Auth Token, you **MUST** set `WEBUI_SECRET_KEY` in Docker config.

### Install and Run

```bash
uvx mcpo --port 8000 -- your_mcp_server_command
```

Example with Time MCP Server:
```bash
uvx mcpo --port 8000 -- uvx mcp-server-time --local-timezone=America/New_York
```

API docs at: `http://localhost:8000/docs`

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install mcpo uv
CMD ["uvx", "mcpo", "--host", "0.0.0.0", "--port", "8000", "--", "uvx", "mcp-server-time", "--local-timezone=America/New_York"]
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If Open WebUI is HTTPS, local server must either use HTTPS or run on localhost.

## Troubleshooting

- **Connection fails**: Check protocol (HTTP vs HTTPS). Modal may pre-fill `https://`.
- **Localhost issues**: For User Tool Servers, `localhost` means the browser machine. For Global, it means the backend server. In Docker, use `host.docker.internal`.
- **CORS errors**: Add CORS middleware to tool server.

## FAQ

- **Any framework works**: FastAPI, Flask, Express, Spring Boot, Go. Just expose valid OpenAPI schema with custom `operationId` per endpoint.
- **Security**: Use OAuth 2.0, API Keys, JWT, Basic Auth. Use HTTPS in production.
- **Multiple servers**: Each runs independently with own OpenAPI schema.
- **Existing MCP server?**: Use mcpo bridge: `uvx mcpo --port 8000 -- uvx mcp-server-time`
- **Single server, multiple tools**: Yes, group related capabilities under different endpoints in one schema.
