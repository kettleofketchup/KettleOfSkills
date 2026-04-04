# Events: __event_emitter__ and __event_call__

Events are real-time notifications or interactive requests sent from backend code (Tool, or Function) to the web UI.

- `__event_emitter__`: one-way updates (fire and forget)
- `__event_call__`: needs user input or response (confirmation, input, execute)

## Basic Usage

```python
await __event_emitter__({"type": "status", "data": {"description": "Processing!", "done": False, "hidden": False}})
```

```python
result = await __event_call__({"type": "input", "data": {"title": "Enter password", "message": "Required", "placeholder": "Your password"}})
```

`__event_call__` timeout is configurable via `WEBSOCKET_EVENT_CALLER_TIMEOUT` (default: 300s).

## Event Payload Structure

```json
{"type": "event_type", "data": { ... }}
```

## Full Event Types List

| type | When to use | Data payload |
| ---- | ----------- | ------------ |
| `status` | Status update/progress | `{description, done: bool, hidden: bool}` |
| `chat:completion` | Chat completion result | (Custom) |
| `chat:message:delta` / `message` | Append content to message | `{content: "text"}` |
| `chat:message` / `replace` | Replace entire message content | `{content: "text"}` |
| `files` / `chat:message:files` | Set/overwrite message files | `{files: [...]}` |
| `chat:title` | Update chat title | `{title: "..."}` |
| `chat:tags` | Update chat tags | `{tags: [...]}` |
| `source` / `citation` | Add source/citation | Source object |
| `notification` | Show toast notification | `{type: "info"/"success"/"error"/"warning", content: "..."}` |
| `confirmation` (needs `__event_call__`) | OK/Cancel dialog | `{title, message}` |
| `input` (needs `__event_call__`) | Input box dialog | `{title, message, placeholder, value, type: "password"}` |
| `execute` (both helpers) | Run JavaScript in browser | `{code: "..."}` |
| `chat:message:favorite` | Update favorite/pin status | `{favorite: bool}` |

## Status Event Details

- `done: false` = shimmer animation (processing)
- `done: true` = static text (complete)
- `hidden: true` = saved but not shown in UI
- Always emit final `done: True` to stop shimmer

## Notification

```python
await __event_emitter__({"type": "notification", "data": {"type": "info", "content": "Operation complete!"}})
```

## Confirmation (requires __event_call__)

```python
result = await __event_call__({"type": "confirmation", "data": {"title": "Are you sure?", "message": "Proceed?"}})
if result:
    # user confirmed
```

## Input (requires __event_call__)

Supports masked password input with `"type": "password"`:

```python
result = await __event_call__({"type": "input", "data": {"title": "Enter API Key", "message": "Required", "placeholder": "sk-...", "type": "password"}})
```

## Execute Event (both helpers)

Runs JavaScript in the user's browser using `new Function()`. Full access to DOM, cookies, localStorage. Not sandboxed.

With `__event_call__` (two-way, returns value):
```python
result = await __event_call__({"type": "execute", "data": {"code": "return document.title;"}})
```

With `__event_emitter__` (fire-and-forget):
```python
await __event_emitter__({"type": "execute", "data": {"code": "/* trigger download */"}})
```

Use `__event_emitter__` for iOS PWA compatibility with downloads.

## External Tool Events

External tools (OpenAPI/MCP) can emit events via REST endpoint. Requires `ENABLE_FORWARD_USER_INFO_HEADERS=True`.

Headers provided: `X-Open-WebUI-Chat-Id`, `X-Open-WebUI-Message-Id`

**Endpoint:** `POST /api/v1/chats/{chat_id}/messages/{message_id}/event`

Supported types: `status`, `notification`, `message`, `replace`, `files`, `source`/`citation`.
Interactive events (`input`, `confirmation`) are NOT supported for external tools.

```python
httpx.post(
    f"http://open-webui-host/api/v1/chats/{chat_id}/messages/{message_id}/event",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"type": "status", "data": {"description": "Working...", "done": False}}
)
```

## Persistence & Browser Disconnection

Server-side execution continues if browser tab closes. No execution timeout on tasks.

### Persisted event types (survive tab close)

| Type | What's saved |
|------|-------------|
| `status` | Appended to `statusHistory` |
| `message` | Appended to `content` |
| `replace` | Overwrites `content` |
| `embeds` | Appended to `embeds` |
| `files` | Appended to `files` |
| `source` | Appended to `sources` |

Use short names for persistence. `"chat:message:embeds"` won't persist but `"embeds"` will.

### Not persisted (Socket.IO only)
`chat:completion`, `chat:message:delta`, `chat:message`, `chat:message:files`, `notification`, `chat:title`, `chat:tags`

### Requires live connection (will error on tab close)
`confirmation`, `input`, `execute` via `__event_call__`

## Function Type Capabilities

| Capability | Tools | Actions | Pipes | Filters |
|-----------|-------|---------|-------|---------|
| `__event_emitter__` | Yes | Yes | Yes | Yes |
| `__event_call__` | Yes | Yes | Yes | Yes |
| Return value to user | Yes | Yes | Yes | No (modifies form_data) |
| HTMLResponse Rich UI | Yes | Yes | No | No |

## Pipes: Return Value vs Events

For Pipes, return/yield content directly. Events like `status`, `source`, `files` work alongside return/yield. Avoid `chat:message:delta` as sole content delivery -- frontend save can overwrite event-emitter-written content.
