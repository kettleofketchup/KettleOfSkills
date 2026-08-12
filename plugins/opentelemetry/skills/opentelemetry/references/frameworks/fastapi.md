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

See [fastapi-advanced.md](fastapi-advanced.md) for background task context propagation, Pydantic spans, and common mistakes.
