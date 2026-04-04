# Filter Functions - Stream, Outlet, and Examples

## Stream Hook (New in Open WebUI 0.5.17)

The `stream` function intercepts and modifies streamed model responses in real time, operating on individual chunks as received.

Use cases: real-time content filtering, live word replacement, streaming analytics, progress indicators, debugging.

### Logging Streaming Chunks

```python
def stream(self, event: dict) -> dict:
    print(event)
    return event
```

Example streamed events:
```jsonl
{"id": "chatcmpl-xxx","choices": [{"delta": {"content": "Hi"}}]}
{"id": "chatcmpl-xxx","choices": [{"delta": {"content": "!"}}]}
{"id": "chatcmpl-xxx","choices": [{"delta": {"content": " :)"}}]}
```

### Filtering Emojis from Streamed Data

```python
def stream(self, event: dict) -> dict:
    for choice in event.get("choices", []):
        delta = choice.get("delta", {})
        if "content" in delta:
            delta["content"] = delta["content"].replace("emoji_char", "")
    return event
```

## Outlet Function (Output Post-Processing)

The `outlet` is like a proofreader. Tidies up AI response after processing.

Input `body` contains **all current messages** in the chat.

**Note:** `outlet()` is **only triggered for WebUI chat requests**, not for direct API calls to `/api/chat/completions`.

Use cases: response logging, token usage tracking, Langfuse/observability integration, citation formatting, disclaimer injection, response caching, quality scoring.

```python
def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
    for message in body["messages"]:
        message["content"] = message["content"].replace("<API_KEY>", "[REDACTED]")
    return body
```

## Valves with Dropdown Menus (Enums)

Use `json_schema_extra` with `enum` for dropdown options:

```python
class Filter:
    class Valves(BaseModel):
        selected_theme: str = Field(
            "Monochromatic Blue",
            description="Choose a color theme",
            json_schema_extra={"enum": ["Plain", "Monochromatic Blue", "Warm", "Cool"]},
        )
        colorize_type: str = Field(
            "sequential_word",
            description="How to apply colors",
            json_schema_extra={"enum": ["sequential_word", "sequential_line", "per_letter", "full_message"]},
        )
```

## Example: Add System Context

```python
class Filter:
    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        context_message = {
            "role": "system",
            "content": "You're a software troubleshooting assistant."
        }
        body.setdefault("messages", []).insert(0, context_message)
        return body
```

## Example: Rate Limiting

```python
class Filter:
    class Valves(BaseModel):
        requests_per_minute: int = Field(default=60)

    def __init__(self):
        self.valves = self.Valves()
        self.user_requests = {}

    def inlet(self, body: dict, __user__: dict = None) -> dict:
        if not __user__:
            return body
        user_id = __user__.get("id")
        current_time = time.time()
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        self.user_requests[user_id] = [t for t in self.user_requests[user_id] if current_time - t < 60]
        if len(self.user_requests[user_id]) >= self.valves.requests_per_minute:
            raise Exception(f"Rate limit exceeded: {self.valves.requests_per_minute} requests/minute")
        self.user_requests[user_id].append(current_time)
        return body
```

## Recommended Filter Organization

```
Global Always-On Filters:
  - PII Scrubber (security)
  - Content Moderator (compliance)
  - Request Logger (analytics)

Model-Specific Always-On Filters:
  - Code Formatter (for coding models only)
  - Medical Terminology Corrector (for medical models)

Toggleable Filters (User Choice):
  - Web Search Integration
  - Citation Mode
  - Translation Filter
  - Verbose Output Mode
```

## Best Practices

**Use global filters for:** Security/compliance, system-wide formatting, logging/analytics, org-wide policies.

**Use toggleable filters for:** User-controlled features (web search, translation), optional enhancements, features with performance cost.

## Filters vs Pipe Functions

Filters modify data going to/from models but do not significantly interact with logic outside these phases. Pipes can integrate external APIs or transform backend operations, exposing as entirely new "models."

Heavy post-processing should use a Pipe Function instead of outlet.
