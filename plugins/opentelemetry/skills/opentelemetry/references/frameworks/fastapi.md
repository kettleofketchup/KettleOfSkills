---
last_updated: 2026-03-08
---

# FastAPI OpenTelemetry Instrumentation

## Auto-Instrumentation

### Install

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-sqlalchemy opentelemetry-instrumentation-asyncpg \
    opentelemetry-instrumentation-httpx opentelemetry-instrumentation-aiohttp-client
```

### Zero-Code (CLI)

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
opentelemetry-instrument --service_name my-fastapi-app uvicorn main:app
```

Env vars: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_TRACES_EXPORTER=otlp`.

## FastAPIInstrumentor Setup

```python
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
```

### Full Configuration with Lifespan

```python
from contextlib import asynccontextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

@asynccontextmanager
async def lifespan(app: FastAPI):
    resource = Resource.create({"service.name": "my-api", "service.version": "1.0.0"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
        endpoint="otel-collector:4317", insecure=True)))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        excluded_urls="health,ready",                      # comma-separated regex
        server_request_hook=lambda span, scope: span.set_attribute("custom.path", scope.get("path", "")),
        client_request_hook=lambda span, scope: None,
        client_response_hook=lambda span, msg: None,
        http_capture_headers_server_request=["x-request-id"],
        http_capture_headers_server_response=["content-type"],
    )
    yield
    provider.shutdown()  # flush pending spans, close exporters

app = FastAPI(lifespan=lifespan)
```

Env var for exclusions: `OTEL_PYTHON_FASTAPI_EXCLUDED_URLS="health,metrics"`.

## Custom Spans in Route Handlers

```python
from opentelemetry import trace

tracer = trace.get_tracer("my-api.routes")

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    with tracer.start_as_current_span("fetch-user", attributes={"user.id": user_id}) as span:
        user = await db.get_user(user_id)
        if not user:
            span.set_status(trace.StatusCode.ERROR, "user not found")
            span.add_event("user.missing", {"user.id": user_id})
            raise HTTPException(404)
        span.set_attribute("user.role", user.role)
        return user
```

## SQLAlchemy / asyncpg Tracing

```python
from sqlalchemy.ext.asyncio import create_async_engine
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

engine = create_async_engine("postgresql+asyncpg://user:pass@db:5432/mydb")
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)  # must use .sync_engine
AsyncPGInstrumentor().instrument()  # driver-level, catches all queries globally
```

Use both for full coverage: SQLAlchemy = ORM-level spans, asyncpg = raw driver spans.

## httpx / aiohttp Client Tracing

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor

# Global — patches all clients automatically
HTTPXClientInstrumentor().instrument()
AioHttpClientInstrumentor().instrument()

# Per-client (httpx only)
async with httpx.AsyncClient() as client:
    HTTPXClientInstrumentor.instrument_client(client)
    resp = await client.get("https://api.example.com/data")
```

Context propagation (traceparent/tracestate) injected automatically for all instrumented clients.

## Dependency Injection — Passing Tracer

```python
from fastapi import Depends, Request
from opentelemetry import trace

def get_tracer() -> trace.Tracer:
    return trace.get_tracer("my-api.deps")

def get_current_span() -> trace.Span:
    return trace.get_current_span()

@app.get("/orders")
async def list_orders(tracer: trace.Tracer = Depends(get_tracer)):
    with tracer.start_as_current_span("list-orders-query"):
        return await db.fetch_orders()
```

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
