# Plugins & Extensibility Reference

## Plugin Types

| Type | Purpose | User Level |
|------|---------|------------|
| Tools | Grant LLMs external capabilities (APIs, data) | Users with permissions |
| Functions | Extend WebUI platform (custom models, filters, buttons) | Admins only |
| Pipelines | Transform features into API-compatible workflows | Expert users |

**Security**: All plugins execute arbitrary Python on the server. Review code before installation.

## Functions (Three Types)

### Pipe Functions (Custom Agents/Models)
Appear as selectable models. Integrate external APIs, combine model outputs, create custom workflows.

### Filter Functions (Modify I/O)
- **Inlet**: Transform input before sending to model
- **Outlet**: Modify output before displaying

### Action Functions (Custom Buttons)
Add interactive buttons beneath chat messages for one-click functionality.

### Enablement
- **Pipe**: Available as standalone model once enabled
- **Filter/Action**: Assign to specific models via Workspace > Models, or enable globally via Workspace > Functions

## Valves (Configuration)

| Feature | Valves | UserValves |
|---------|--------|-----------|
| Access | Admin-only | Any user |
| Scope | System-wide | Per-user |
| Code Access | `self.valves.field` | `__user__["valves"].field` |

### Field Types
```python
from pydantic import BaseModel, Field

class Tools:
    class Valves(BaseModel):
        api_key: str = Field(default="", description="API key",
            json_schema_extra={"input": {"type": "password"}})
        priority: str = Field(default="medium",
            json_schema_extra={"input": {"type": "select",
                "options": ["low", "medium", "high"]}})
    class UserValves(BaseModel):
        preference: str = Field(default="concise")
    def __init__(self):
        self.valves = self.Valves()
```

Supports: password, select (static/dynamic with `options` method), Literal for multi-choice.

## Reserved Arguments

| Argument | Type | Purpose |
|----------|------|---------|
| `body` | dict | Request body (stream, model, messages, files) |
| `__user__` | dict | User info (id, email, name, role, valves) |
| `__metadata__` | dict | Chat/model/file info, variables, interface |
| `__model__` | dict | Model config and metadata |
| `__messages__` | list | Previous conversation messages |
| `__chat_id__` | str | Chat identifier |
| `__event_emitter__` | Callable | Fire-and-forget event display |
| `__event_call__` | Callable | Interactive event (waits for response) |
| `__files__` | list | Attached files (binary excluded for perf) |
| `__task__` | str | Task type (title_generation, function_calling, etc.) |
| `__tools__` | list | Available tool instances |

File path: `/app/backend/data/uploads/{file_id}_{filename}`

## Event System

### Event Types

| Type | Purpose | Persisted |
|------|---------|-----------|
| `status` | Progress tracking (shimmer animation) | Yes |
| `chat:message:delta` | Stream text incrementally | Yes |
| `chat:message` | Replace entire message content | Yes |
| `files` | Attach files to message | Yes |
| `source`/`citation` | Add references/citations | Yes |
| `notification` | Toast messages (info/warning/error/success) | No |
| `confirmation` | Yes/no dialog (`__event_call__`) | No |
| `input` | Text input prompt (`__event_call__`) | No |
| `chat:title` | Update chat title | No |
| `chat:tags` | Update chat tags | No |
| `execute` | Run JavaScript in browser | No |

### Common Pattern
```python
await __event_emitter__({"type": "status", "data": {"description": "Processing...", "done": False}})
for chunk in response:
    await __event_emitter__({"type": "chat:message:delta", "data": {"content": chunk}})
await __event_emitter__({"type": "status", "data": {"description": "Done", "done": True}})
```

**Critical**: Always emit `done: True` to stop shimmer animations.

### External Tool Events
```
POST /api/v1/chats/{chat_id}/messages/{message_id}/event
Authorization: Bearer YOUR_API_KEY
```
Requires `ENABLE_FORWARD_USER_INFO_HEADERS=True`.

---

## MCP (Model Context Protocol)

Native support since v0.6.31+.

### Setup
1. Admin Settings > External Tools > + Add Server
2. Type: **MCP (Streamable HTTP)**
3. Enter Server URL and Auth
4. Save

### Authentication Modes
| Mode | Use Case |
|------|----------|
| None | Local/internal servers |
| Bearer | Servers requiring API token |
| OAuth 2.1 | Dynamic Client Registration |
| OAuth 2.1 (Static) | Pre-created client ID/secret |

**Critical**: Do NOT set OAuth 2.1 MCP tools as default/pre-enabled on models (consent flow can't execute during chat).

### Docker Networking
Use `http://host.docker.internal:<port>` for host MCP servers.

### Transport
Only **Streamable HTTP** supported. For stdio/SSE servers, use **mcpo** proxy.

---

## OpenAPI Tool Servers

Connect external OpenAPI-compatible servers as tool providers.

### User vs Admin Tool Servers
- **User Tool Server** (Settings > Tools): Browser-to-server, personal
- **Global Tool Server** (Admin Settings > Integrations): Backend-to-server, all users

### Auth Types
| Type | Description |
|------|-------------|
| None | No auth |
| Bearer Token | API key in Authorization header |
| System OAuth | Uses OAuth session token from login |

---

## Pipelines

External processing layer running as separate container. Offloads compute-intensive tasks.

### Architecture
```
User ↔ Open WebUI ↔ Pipelines Container ↔ External Services
```

### Types
- **Pipe Pipelines**: Custom model endpoints
- **Filter Pipelines**: Inlet/outlet message processing
- **Pipeline Valves**: Runtime-configurable settings

### Docker Compose
```yaml
services:
  pipelines:
    image: ghcr.io/open-webui/pipelines:main
    ports: ["9099:9099"]
    volumes:
      - pipelines:/app/pipelines
  open-webui:
    environment:
      - OPENAI_API_BASE_URLS=http://pipelines:9099;https://api.openai.com/v1
      - OPENAI_API_KEYS=0p3n-w3bu!;sk-xxx
```
