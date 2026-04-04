# Tool Development

Toolkits are defined in a single Python file, with a top level docstring with metadata and a `Tools` class.

Tool methods should generally be defined as `async`.

## Example Top-Level Docstring

```python
"""
title: String Inverse
author: Your Name
author_url: https://website.com
git_url: https://github.com/username/string-reverse.git
description: This tool calculates the inverse of a string
required_open_webui_version: 0.4.0
requirements: langchain-openai, langgraph, ollama, langchain_ollama
version: 0.4.0
licence: MIT
"""
```

## Tools Class

```python
class Tools:
    def __init__(self):
        self.valves = self.Valves()

    class Valves(BaseModel):
        api_key: str = Field("", description="Your API key here")

    def reverse_string(self, string: str) -> str:
        """
        Reverses the input string.
        :param string: The string to reverse
        """
        if self.valves.api_key != "42":
            return "Wrong API key"
        return string[::-1]
```

### Type Hints
Each tool must have type hints for arguments. Types may be nested, e.g., `queries_and_docs: list[tuple[str, int]]`. Type hints generate the JSON schema sent to the model. Tools without type hints work with much less consistency.

### Valves and UserValves (optional, highly encouraged)
Valves are admin-configurable via Tools/Functions menus. UserValves are user-configurable from chat sessions.

### Optional Arguments

- `__event_emitter__`: Emit events (status, notifications, etc.)
- `__event_call__`: Like event emitter but for user interactions. Timeout configurable via `WEBSOCKET_EVENT_CALLER_TIMEOUT` (default: 300s).
- `__user__`: Dictionary with user info. Contains `UserValves` in `__user__["valves"]`.
- `__metadata__`: Dictionary with chat metadata
- `__messages__`: List of previous messages
- `__files__`: Attached files
- `__model__`: Dictionary with model information
- `__oauth_token__`: User's valid, auto-refreshed OAuth token payload (contains `access_token`, `id_token`, etc.)

### Using OAuth Token in a Tool

```python
class Tools:
    async def get_user_profile_from_external_api(self, __oauth_token__: Optional[dict] = None) -> str:
        """
        Fetches user profile using OAuth access token.
        :param __oauth_token__: Injected by Open WebUI.
        """
        if not __oauth_token__ or "access_token" not in __oauth_token__:
            return "Error: User is not authenticated via OAuth."
        access_token = __oauth_token__["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.my-service.com/v1/profile", headers=headers)
            response.raise_for_status()
            return f"API Response: {response.json()}"
```

## Event Emitters

Event Emitters add additional information to the chat interface. Unlike Filter Outlets, they can append but not strip information. Emitters can be activated at any stage during the Tool.

### Function Calling Mode Compatibility

| Event Type | Default Mode | Native Mode | Status |
|------------|-------------|-------------|--------|
| `status` | Full support | Identical | COMPATIBLE |
| `message` | Full support | BROKEN (overwritten) | INCOMPATIBLE |
| `chat:completion` | Full support | LIMITED | PARTIALLY COMPATIBLE |
| `chat:message:delta` | Full support | BROKEN | INCOMPATIBLE |
| `chat:message` / `replace` | Full support | BROKEN | INCOMPATIBLE |
| `files` | Full support | Identical | COMPATIBLE |
| `chat:message:error` | Full support | Identical | COMPATIBLE |
| `chat:message:follow_ups` | Full support | Identical | COMPATIBLE |
| `notification` | Full support | Identical | COMPATIBLE |
| `confirmation` | Full support | Identical | COMPATIBLE |
| `execute` | Full support | Identical | COMPATIBLE |
| `input` | Full support | Identical | COMPATIBLE |
| `citation` / `source` | Full support | Identical | COMPATIBLE |

In **Native Mode**, completion snapshots overwrite tool-emitted content updates. Use `status`, `citation`, `notification` for Native Mode compatibility.

### Status Events (Compatible in both modes)

```python
await __event_emitter__({
    "type": "status",
    "data": {"description": "Processing...", "done": False, "hidden": False}
})
```

Always emit a final `done: True` status to stop shimmer animation.

### Citations (Compatible in both modes)

```python
class Tools:
    def __init__(self):
        self.citation = False  # REQUIRED - prevents automatic citations overriding custom ones

    async def research_tool(self, topic: str, __event_emitter__=None) -> str:
        await __event_emitter__({
            "type": "citation",
            "data": {
                "document": ["content text"],
                "metadata": [{"date_accessed": "...", "source": "title", "url": "https://..."}],
                "source": {"name": "title", "url": "https://..."}
            }
        })
        return "Research completed."
```

Set `self.citation = False` to prevent automatic citations from overriding custom ones.

### Mode-Safe Tool Pattern

```python
async def universal_tool(self, prompt: str, __event_emitter__=None, __metadata__=None) -> str:
    is_native_mode = __metadata__ and __metadata__.get("params", {}).get("function_calling") == "native"
    if __event_emitter__:
        if is_native_mode:
            await __event_emitter__({"type": "status", "data": {"description": "Processing...", "done": False}})
        else:
            await __event_emitter__({"type": "message", "data": {"content": "Processing..."}})
    await __event_emitter__({"type": "status", "data": {"description": "Completed", "done": True}})
    return "Tool execution completed"
```
