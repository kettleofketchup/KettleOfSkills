# Action Functions

Action functions allow you to write custom buttons that appear in the message toolbar. This enables interactive messaging: granting permission before a task, generating visualizations, downloading audio snippets, and more.

Action functions should always be defined as `async`.

## Action Function Architecture

Actions are Python-based functions that integrate into the chat message toolbar. They execute server-side and can interact with users through real-time events, modify message content, and access the full Open WebUI context.

### Function Structure

```python
class Action:
    def __init__(self):
        self.valves = self.Valves()

    class Valves(BaseModel):
        parameter_name: str = "default_value"
        priority: int = 0  # Controls button display order (lower = appears first)

    async def action(self, body: dict, __user__=None, __event_emitter__=None, __event_call__=None):
        return {"content": "Modified message content"}
```

### Action Method Parameters

- **`body`** - Dictionary containing the message data and context
- **`__user__`** - Current user object with permissions and settings
- **`__event_emitter__`** - Function to send real-time updates to the frontend
- **`__event_call__`** - Function for bidirectional communication (confirmations, inputs)
- **`__model__`** - Model information that triggered the action
- **`__request__`** - FastAPI request object for accessing headers
- **`__id__`** - Action ID (useful for multi-action functions)

## Event System Integration

### Event Emitter (`__event_emitter__`)

```python
async def action(self, body: dict, __event_emitter__=None):
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Processing request..."}
    })
    await __event_emitter__({
        "type": "notification",
        "data": {"type": "info", "content": "Action completed successfully"}
    })
```

### Event Call (`__event_call__`)

```python
async def action(self, body: dict, __event_call__=None):
    response = await __event_call__({
        "type": "confirmation",
        "data": {"title": "Confirm Action", "message": "Are you sure?"}
    })
    user_input = await __event_call__({
        "type": "input",
        "data": {"title": "Enter Value", "message": "Provide info:", "placeholder": "Type here..."}
    })
```

## Multi-Actions

Functions can define multiple sub-actions through an `actions` array:

```python
actions = [
    {"id": "summarize", "name": "Summarize", "icon_url": "https://example.com/icons/summarize.svg"},
    {"id": "translate", "name": "Translate", "icon_url": "https://example.com/icons/translate.svg"}
]

async def action(self, body: dict, __id__=None, **kwargs):
    if __id__ == "summarize":
        return {"content": "Summary: ..."}
    elif __id__ == "translate":
        return {"content": "Translation: ..."}
```

## Global vs Model-Specific Actions
- **Global Actions** - Toggle in Action settings to enable for all users and models.
- **Model-Specific Actions** - Configure in model settings.

## Button Display Order (Priority)

Buttons are sorted by `priority` valve in **ascending order** (lower = leftmost). Default is `0`. Without priority, actions sort **alphabetically by function ID**.

```python
class Valves(BaseModel):
    priority: int = 0  # Lower = appears first
```

## File and Media Handling

```python
async def action(self, body: dict):
    message = body
    if message.get("files"):
        for file in message["files"]:
            if file["type"] == "image":
                pass
    return {
        "content": "Analysis complete",
        "files": [{"type": "image", "url": "generated_chart.png", "name": "Analysis Chart"}]
    }
```

## User Context and Permissions

```python
async def action(self, body: dict, __user__=None):
    if __user__["role"] != "admin":
        return {"content": "This action requires admin privileges"}
    return {"content": f"Hello {__user__['name']}, admin action completed"}
```

## Frontmatter Fields

- `title`: Display name of the Action.
- `author`: Name of the creator.
- `version`: Version number.
- `required_open_webui_version`: Minimum compatible version.
- `icon_url` (optional): URL pointing to an icon image. Avoid base64 icons -- they bloat the `/api/models` response.
- `requirements`: pip dependencies (e.g., `requests,beautifulsoup4`).

## Error Handling

```python
async def action(self, body: dict, __event_emitter__=None):
    try:
        result = perform_operation()
        return {"content": f"Success: {result}"}
    except Exception as e:
        await __event_emitter__({
            "type": "notification",
            "data": {"type": "error", "content": f"Action failed: {str(e)}"}
        })
        return {"content": "Action encountered an error"}
```

## Best Practices

- Use async/await for I/O operations
- Implement timeouts for external API calls
- Provide progress updates for long-running operations
- Use confirmation dialogs for destructive actions
- Actions can return HTML content via Rich UI Embedding (renders as interactive iframes)
