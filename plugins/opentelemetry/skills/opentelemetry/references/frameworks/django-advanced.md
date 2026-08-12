---
last_updated: 2026-03-08
---

# Django OTEL: Celery, DRF, and Common Mistakes

## Celery Task Tracing

`pip install opentelemetry-instrumentation-celery`, then `CeleryInstrumentor().instrument()` before Celery app created. Context propagation is automatic. Manual propagation if needed:

```python
from opentelemetry.propagate import inject, extract

# Django view — inject trace context into task headers
def submit_order(request, order_id):
    carrier = {}
    inject(carrier)
    process_order.apply_async(args=[order_id], headers=carrier)

# Celery task — extract and continue trace
@app.task(bind=True)
def process_order(self, order_id):
    ctx = extract(self.request.headers)
    with tracer.start_as_current_span("task.process_order", context=ctx) as span:
        span.set_attribute("order.id", order_id)
```

## Django REST Framework

`DjangoInstrumentor` auto-instruments all DRF endpoints. Add custom spans for serialization:

```python
class OrderViewSet(APIView):
    def get(self, request, pk):
        with tracer.start_as_current_span("drf.serialize") as span:
            order = Order.objects.get(pk=pk)
            serializer = OrderSerializer(order)
            span.set_attribute("serializer", "OrderSerializer")
        return Response(serializer.data)
```

DRF exception handler with OTEL error recording:

```python
def otel_exception_handler(exc, context):
    span = trace.get_current_span()
    span.record_error(exc)
    span.set_status(trace.StatusCode.ERROR, str(exc))
    return exception_handler(exc, context)
# settings.py: REST_FRAMEWORK = {"EXCEPTION_HANDLER": "myapp.utils.otel_exception_handler"}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `.instrument()` after Django loads | Call in `manage.py` before `execute_from_command_line()` or top of `wsgi.py` |
| `request.user` in `request_hook` | Use `response_hook` — `AuthenticationMiddleware` hasn't run yet |
| Forget `opentelemetry-bootstrap` | DB/cache/HTTP client libs stay uninstrumented |
| Instrument in `settings.py` | Too early — SDK not ready. Use `manage.py` or `AppConfig.ready()` |
| No health check exclusion | `OTEL_PYTHON_DJANGO_EXCLUDED_URLS=health,ready,metrics` |
| `AlwaysSample` in production | `parentbased_traceidratio` + `OTEL_TRACES_SAMPLER_ARG=0.1` |
| ORM loop span explosion | Each query = span. Use `select_related`/`prefetch_related` |
| sqlcommenter not working | Pass `is_sql_commentor_enabled=True` to `.instrument()` |
| ASGI app with WSGI instrumentor | Use `opentelemetry-instrumentation-asgi` for Daphne/Uvicorn |
| Lost context in threads | Pass context explicitly; copy `contextvars` in `ThreadPoolExecutor` |
