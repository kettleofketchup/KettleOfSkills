# Migration Guide: Open WebUI 0.4 to 0.5

## What Changed

- **Old Architecture**: Sub-app architecture with separate FastAPI applications (e.g., `ollama`, `openai`).
- **New Architecture**: Single FastAPI app with multiple routers.

### Key Changes

1. **Apps moved to Routers**: `open_webui.apps` -> `open_webui.routers`
2. **Main app simplified**: `open_webui.apps.webui` -> `open_webui.main`
3. **Unified API Endpoint**: `chat_completion` in `open_webui.main` replaces separate functions. Direct successor is `generate_chat_completion` from `open_webui.utils.chat`.
4. **Updated Function Signatures**: Now require a `request` object via `__request__` parameter.

## Import Path Changes

| Old Path | New Path |
|----------|----------|
| `open_webui.apps.ollama` | `open_webui.routers.ollama` |
| `open_webui.apps.openai` | `open_webui.routers.openai` |
| `open_webui.apps.audio` | `open_webui.routers.audio` |
| `open_webui.apps.retrieval` | `open_webui.routers.retrieval` |
| `open_webui.apps.webui` | `open_webui.main` |

Special case for webui models:
```python
# Before (0.4):
from open_webui.apps.webui.models import SomeModel
# After (0.5):
from open_webui.models import SomeModel
```

## Updating Imports

```python
# Before:
from open_webui.apps.ollama import main as ollama
from open_webui.apps.openai import main as openai

# After - separate router imports:
from open_webui.routers.ollama import generate_chat_completion
from open_webui.routers.openai import generate_chat_completion

# After - unified endpoint:
from open_webui.main import chat_completion
```

## Choosing Between Endpoints

### `open_webui.main.chat_completion`
- Simulates POST request to `/api/chat/completions`
- Processes files, tools, and other tasks
- Best for complete API flow

### `open_webui.utils.chat.generate_chat_completion`
- Direct POST request without extra parsing
- Direct successor to previous `ollama.generate_chat_completion` and `openai.generate_chat_completion`
- Best for lightweight scenarios

```python
from open_webui.main import chat_completion                     # Full API flow
from open_webui.utils.chat import generate_chat_completion      # Lightweight direct
```

## Function Signature Changes

| Old | Direct Successor (New) | Unified Option (New) |
|-----|----------------------|---------------------|
| `openai.generate_chat_completion(form_data, user)` | `generate_chat_completion(request, form_data, user)` | `chat_completion(request, form_data, user)` |

## Refactoring Example

### Before (0.4):

```python
from pydantic import BaseModel
from open_webui.apps.ollama import generate_chat_completion

class User(BaseModel):
    id: str
    email: str
    name: str
    role: str

class Pipe:
    def __init__(self):
        pass

    async def pipe(self, body: dict, __user__: dict) -> str:
        user = User(**__user__)
        body["model"] = "llama3.2:latest"
        return await ollama.generate_chat_completion(body, user)
```

### After (0.5):

```python
from pydantic import BaseModel
from fastapi import Request
from open_webui.utils.chat import generate_chat_completion

class User(BaseModel):
    id: str
    email: str
    name: str
    role: str

class Pipe:
    def __init__(self):
        pass

    async def pipe(self, body: dict, __user__: dict, __request__: Request) -> str:
        user = User(**__user__)
        body["model"] = "llama3.2:latest"
        return await generate_chat_completion(__request__, body, user)
```

## Summary

- **Apps to Routers**: Replace `open_webui.apps` with `open_webui.routers` (except `webui` -> `open_webui.main`)
- **Unified Endpoint**: Use `open_webui.main.chat_completion` for simplicity
- **Function Signatures**: Pass the `request` object via `__request__`
