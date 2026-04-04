# Filter Functions

Filters modify data *before it's sent to the LLM* (input) or *after it's returned from the LLM* (output).

1. **Inlet Function**: Tweak input data before it reaches the AI model.
2. **Stream Function**: Capture and adjust AI responses as they're generated (new in 0.5.17).
3. **Outlet Function**: Adjust the AI's response after processing, before showing to user.

## Basic Skeleton

```python
from pydantic import BaseModel
from typing import Optional

class Filter:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict) -> dict:
        print(f"inlet called: {body}")
        return body

    def stream(self, event: dict) -> dict:
        print(f"stream event: {event}")
        return event

    def outlet(self, body: dict) -> None:
        print(f"outlet called: {body}")
```

## Toggle Filter (New in 0.6.10)

Filters can expose UI toggles and display custom icons:

```python
class Filter:
    def __init__(self):
        self.valves = self.Valves()
        self.toggle = True  # Creates a switch UI in Open WebUI
        self.icon = "https://example.com/icons/lightbulb.svg"

    async def inlet(self, body: dict, __event_emitter__, __user__: Optional[dict] = None) -> dict:
        await __event_emitter__({"type": "status", "data": {"description": "Toggled!", "done": True, "hidden": False}})
        return body
```

## Filter Administration

### Filter Activation States

| State | `is_active` | `is_global` | Effect |
|-------|------------|------------|--------|
| **Globally Enabled** | True | True | Applied to ALL models automatically |
| **Globally Disabled** | False | True | Not applied anywhere |
| **Model-Specific** | True | False | Only applied to explicitly enabled models |
| **Inactive** | False | False | Not applied anywhere |

Global + Active filters are **force-enabled** for all models (checked and greyed out in model settings).

### API Endpoint for toggling global:
```http
POST /functions/id/{filter_id}/toggle/global
```

### Two-Tier Filter System

**Tier 1: FiltersSelector** -- Controls which filters are **available** for a model. Saves to `model.meta.filterIds`.

**Tier 2: DefaultFiltersSelector** -- Controls which toggleable filters are **enabled by default**. Only for filters with `self.toggle = True`. Saves to `model.meta.defaultFilterIds`.

### Always-On vs Toggleable Filters

**Always-On** (no `toggle` property): Run automatically, no user control in chat UI. Use for security, compliance, logging, rate limiting.

**Toggleable** (`self.toggle = True`): Appear as switches in chat UI. Users enable/disable per session. Use for web search, citation mode, translation.

## Filter Priority & Execution Order

```python
class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=0, description="Lower values run first.")
```

Filters sort in **ascending** order by priority. Same priority sorts **alphabetically by function ID**.

## Data Passing Between Filters

Each filter receives the **modified data from the previous filter**. Always return the body.

```
User Input -> Filter (priority=0) -> Filter (priority=1) -> Filter (priority=2) -> LLM Request
```

## Filter Behavior with API Requests

| Function | WebUI Request | Direct API Request |
|----------|--------------|-------------------|
| `inlet()` | Always called | Always called |
| `stream()` | Called during streaming | Called during streaming |
| `outlet()` | Called after response | **NOT called** by default |
| `__event_emitter__` | Shows UI feedback | Runs but no UI |

To trigger `outlet()` for API requests, call `/api/chat/completed` after receiving the response.

### Detecting API vs WebUI Requests

```python
def inlet(self, body: dict, __metadata__: dict = None) -> dict:
    interface = __metadata__.get("interface") if __metadata__ else None
    if interface == "open-webui":
        print("Request from WebUI")
    else:
        print("Direct API request")
    return body
```

## Available Dunder Parameters

| Parameter | What it provides |
|-----------|-----------------|
| `__model__` | Full model dict (including `info.base_model_id` for workspace models) |
| `__user__` | User data (`id`, `email`, `name`, `role`) |
| `__metadata__` | Request metadata (`chat_id`, `session_id`, `interface`, etc.) |
| `__event_emitter__` | Function to send status updates, embeds, etc. |
| `__chat_id__` | Chat session ID |
| `__request__` | Raw FastAPI `Request` object |

## Injecting Extra API Body Parameters

Inlet filters can inject extra fields into the request body that get forwarded to the LLM API. Only internal keys like `metadata`, `features`, `tool_ids`, `files`, `skill_ids` are removed.

```python
class Filter:
    def inlet(self, body: dict, __user__: dict = None) -> dict:
        if __user__ and __user__.get("id"):
            body["safety_identifier"] = hashlib.sha256(__user__["id"].encode()).hexdigest()
        return body
```

Filters can only modify the request body, not outbound HTTP headers.

## Resolving the Base Model

```python
class Filter:
    def inlet(self, body: dict, __model__: dict = None) -> dict:
        base_model_id = None
        if __model__ and "info" in __model__:
            base_model_id = __model__["info"].get("base_model_id")
        return body
```
