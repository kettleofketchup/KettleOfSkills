---
last_updated: 2026-03-08
---

# FastAPI OTEL: Background Tasks, Pydantic, and Common Mistakes

## Background Tasks — Context Propagation

Background tasks run after response sent — OTEL context lost unless explicitly captured.

```python
from opentelemetry import context as otel_context, trace

tracer = trace.get_tracer("my-api.tasks")

def traced_background_task(fn, *args, **kwargs):
    """Wrap background task, capture OTEL context at call site."""
    ctx = otel_context.get_current()
    def wrapper():
        token = otel_context.attach(ctx)
        try:
            with tracer.start_as_current_span(f"background:{fn.__name__}"):
                fn(*args, **kwargs)
        finally:
            otel_context.detach(token)
    return wrapper

@app.post("/notify")
async def notify(bg: BackgroundTasks):
    bg.add_task(traced_background_task(send_email, to="user@example.com"))
    return {"status": "queued"}
```

Without wrapper: background spans become orphaned root spans, not linked to request trace.

## Pydantic Validation Spans (Optional)

No built-in instrumentation. Add manual spans only if validation is a bottleneck:

```python
@app.post("/items")
async def create_item(request: Request):
    with tracer.start_as_current_span("pydantic.validate"):
        item = ItemModel.model_validate(await request.json())  # Pydantic v2
    return await save_item(item)
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Instrument before `FastAPI()` created | Call `instrument_app(app)` after app instantiation |
| Async engine passed to SQLAlchemyInstrumentor | Use `engine.sync_engine` property |
| Background task spans orphaned | Capture and attach OTEL context explicitly |
| `excluded_urls` not working | Regex patterns, not glob — `"health\|ready"` not `"/health*"` |
| Missing spans for sub-dependencies | Propagate tracer context through full `Depends()` chain |
| No spans on shutdown/crash | Call `provider.shutdown()` in lifespan or atexit handler |
| HTTPException details missing from span | Override exception handler, call `span.record_exception(exc)` |
| Duplicate DB spans (SQLAlchemy + asyncpg) | Expected — ORM + driver level. Filter in backend if noisy |
| `instrument()` called twice | Raises error. Guard with `is_instrumented_by_opentelemetry` |
| Header capture not working | Set `http_capture_headers_server_request` or env var `OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST` |
