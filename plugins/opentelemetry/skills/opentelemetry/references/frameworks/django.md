---
last_updated: 2026-03-08
---

# Django OpenTelemetry Instrumentation

## Auto-Instrumentation

```bash
pip install opentelemetry-distro opentelemetry-instrumentation-django opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install  # auto-detect psycopg2, redis, requests, etc.
```

Zero-code — run with wrapper:

```bash
opentelemetry-instrument --service_name my-django-app --traces_exporter otlp \
    --exporter_otlp_endpoint http://otel-collector:4317 python manage.py runserver
```

Programmatic — in `manage.py` before `execute_from_command_line()`, or top of `wsgi.py`/`asgi.py`:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor

resource = Resource.create({"service.name": "my-django-app"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)))
trace.set_tracer_provider(provider)
DjangoInstrumentor().instrument()  # MUST call before Django loads — never in settings.py
```

## DjangoInstrumentor Config

```python
DjangoInstrumentor().instrument(
    request_hook=request_hook,             # called after span created
    response_hook=response_hook,           # called before span ends (after all middleware)
    excluded_urls="health,ready,metrics",  # comma-separated regex
    is_sql_commentor_enabled=True,         # append traceparent to SQL queries
)

def request_hook(span, request):
    span.set_attribute("http.request.id", request.META.get("HTTP_X_REQUEST_ID", ""))

def response_hook(span, request, response):
    # Safe to read request.user here — AuthenticationMiddleware already ran
    if hasattr(request, "user") and request.user.is_authenticated:
        span.set_attribute("enduser.id", str(request.user.pk))
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OTEL_SERVICE_NAME` | `unknown_service` | Service name |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4317` | Collector endpoint |
| `OTEL_PYTHON_DJANGO_EXCLUDED_URLS` | — | URL regex to skip (comma-separated) |
| `OTEL_PYTHON_DJANGO_TRACED_REQUEST_ATTRS` | — | Request attrs as span attrs |
| `OTEL_PYTHON_DJANGO_INSTRUMENT` | `true` | Set `false` to disable |
| `OTEL_TRACES_SAMPLER` | `parentbased_always_on` | Sampler type |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Ratio for `traceidratio` sampler |
| `OTEL_RESOURCE_ATTRIBUTES` | — | Extra attrs, e.g. `deployment.environment=prod` |

## Manual Instrumentation — Custom Spans

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def order_view(request, order_id):
    with tracer.start_as_current_span("process-order") as span:
        span.set_attribute("order.id", order_id)
        order = Order.objects.get(pk=order_id)
        with tracer.start_as_current_span("charge-payment") as pay_span:
            try:
                charge(order)
            except PaymentError as e:
                pay_span.record_error(e)
                pay_span.set_status(trace.StatusCode.ERROR, str(e))
                raise
    return JsonResponse({"status": "ok"})
```

### Middleware and signals — same pattern

```python
# Middleware
class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        with tracer.start_as_current_span("middleware.timing") as span:
            span.set_attribute("http.method", request.method)
            response = self.get_response(request)
            span.set_attribute("http.status_code", response.status_code)
            return response

# Signal
def on_user_created(sender, instance, created, **kwargs):
    if created:
        with tracer.start_as_current_span("signal.user_created") as span:
            span.set_attribute("user.id", str(instance.pk))
            send_welcome_email(instance)
post_save.connect(on_user_created, sender=User)
```

## Database Tracing

Auto via `opentelemetry-bootstrap -a install` — installs `psycopg2`, `asyncpg`, `mysqlclient` instrumentors. Captures SQL text, duration, DB system, connection params. Enable sqlcommenter:

```python
DjangoInstrumentor().instrument(is_sql_commentor_enabled=True)
# SELECT * FROM users /* traceparent='00-abc123...' */
```

Manual ORM span wrapping:

```python
with tracer.start_as_current_span("db.get_active_users") as span:
    span.set_attribute("db.system", "postgresql")
    users = User.objects.filter(is_active=True).select_related("profile")
    span.set_attribute("db.rows_returned", len(users))
```

## Template Rendering Spans

Jinja2 auto-covered by `opentelemetry-instrumentation-jinja2`. Django templates — wrap manually:

```python
with tracer.start_as_current_span("template.render") as span:
    span.set_attribute("template.name", "orders/detail.html")
    html = render_to_string("orders/detail.html", {"order": order}, request=request)
return HttpResponse(html)
```

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
