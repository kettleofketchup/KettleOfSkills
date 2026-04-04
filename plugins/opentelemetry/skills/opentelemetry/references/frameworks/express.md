---
last_updated: 2026-03-08
---

# Node.js Framework Instrumentation (Express, NestJS, Fastify)

## Express.js

### Dependencies

```bash
npm install @opentelemetry/sdk-node @opentelemetry/api \
  @opentelemetry/exporter-trace-otlp-http \
  @opentelemetry/instrumentation-http \
  @opentelemetry/instrumentation-express
```

### Bootstrap File (tracing.js)

Load before app code via `node --require ./tracing.js app.js` (CJS) or `node --import ./tracing.mjs app.mjs` (ESM).

```javascript
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');
const { Resource } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');

const sdk = new NodeSDK({
  resource: new Resource({ [ATTR_SERVICE_NAME]: 'my-express-api' }),
  traceExporter: new OTLPTraceExporter({
    url: 'http://otel-collector:4318/v1/traces',
  }),
  instrumentations: [new HttpInstrumentation(), new ExpressInstrumentation()],
});
sdk.start();
process.on('SIGTERM', () => sdk.shutdown());
```

### Auto-Instrumentation (Zero-Code)

No tracing.js needed — meta-package handles everything:

```bash
OTEL_SERVICE_NAME=my-api OTEL_TRACES_EXPORTER=otlp \
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
node --require @opentelemetry/auto-instrumentations-node/register app.js
```

### Manual Spans in Route Handlers

```javascript
const { trace, SpanStatusCode, context } = require('@opentelemetry/api');
const tracer = trace.getTracer('my-express-api');

app.post('/checkout', async (req, res, next) => {
  const activeSpan = trace.getSpan(context.active()); // auto-created by Express instrumentation
  activeSpan?.setAttribute('checkout.user_id', req.body.userId);

  const span = tracer.startSpan('process-payment');
  try {
    const result = await processPayment(req.body);
    span.setAttribute('payment.tx_id', result.txId);
    res.json(result);
  } catch (err) {
    span.recordException(err);
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    next(err);
  } finally {
    span.end();
  }
});
```

### Error Middleware

```javascript
app.use((err, req, res, next) => {
  const span = trace.getSpan(context.active());
  if (span) {
    span.recordException(err);
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    span.setAttribute('error.type', err.constructor.name);
  }
  res.status(err.status || 500).json({ error: err.message });
});
```

## NestJS

OTEL must initialize before NestJS imports modules: `node --require ./tracing.js dist/main.js`

Add to tracing.js instrumentations:

```javascript
const { NestInstrumentation } = require('@opentelemetry/instrumentation-nestjs-core');
instrumentations: [new HttpInstrumentation(), new ExpressInstrumentation(), new NestInstrumentation()],
```

### Interceptor Pattern

```typescript
@Injectable()
export class TracingInterceptor implements NestInterceptor {
  private tracer = trace.getTracer('nestjs-app');
  intercept(ctx: ExecutionContext, next: CallHandler): Observable<any> {
    const span = this.tracer.startSpan(`${ctx.getClass().name}.${ctx.getHandler().name}`);
    return next.handle().pipe(
      tap(() => span.end()),
      catchError((err) => { span.recordException(err); span.setStatus({ code: SpanStatusCode.ERROR }); span.end(); throw err; }),
    );
  }
}
```

### nestjs-otel Module (Community)

```typescript
// app.module.ts
@Module({ imports: [OpenTelemetryModule.forRoot({ metrics: { apiMetrics: { enable: true } } })] })
export class AppModule {}

// service — @Span decorator auto-creates spans
@Injectable()
export class OrderService {
  @Span('OrderService.create')
  async createOrder(dto: CreateOrderDto) { /* ... */ }
}
```

## Fastify

`@opentelemetry/instrumentation-fastify` deprecated June 2025. Use `@fastify/otel`:

```javascript
// otel.js
const { FastifyOtelInstrumentation } = require('@fastify/otel');
const fastifyOtel = new FastifyOtelInstrumentation({ servername: 'my-fastify-api' });

// NodeSDK config
instrumentations: [new HttpInstrumentation(), fastifyOtel],

// app.js — register before routes
await app.register(fastifyOtel.plugin());
app.get('/health', (req) => {
  const { span } = req.openTelemetry();
  span.setAttribute('health.status', 'ok');
  return { status: 'ok' };
});
```

## Common Node.js Patterns

### diagnostics_channel

Node.js core and undici emit events via `node:diagnostics_channel`. OTEL subscribes instead of monkey-patching. `@opentelemetry/instrumentation-undici` traces `fetch()` and undici automatically:

```javascript
instrumentations: [new UndiciInstrumentation(), new HttpInstrumentation()],
```

### HTTP Client Tracing

`traceparent` auto-injected. `http`/`https` via `HttpInstrumentation`, `fetch()`/undici via `UndiciInstrumentation`, axios/got/node-fetch auto-detected (use `http` internally).

### Database Tracing

| ORM/Driver | Package | Notes |
|-----------|---------|-------|
| Prisma | `@prisma/instrumentation` | Also add `previewFeatures: ["tracing"]` in schema.prisma |
| TypeORM | Auto-detected | Via underlying pg/mysql driver instrumentation |
| Knex | `@opentelemetry/instrumentation-knex` | Query builder operation spans |
| pg | `@opentelemetry/instrumentation-pg` | Raw query spans with parameters |
| Mongoose | `@opentelemetry/instrumentation-mongoose` | MongoDB operation spans |

### Context Propagation (AsyncLocalStorage)

`AsyncLocalStorage` is default context manager. Context flows automatically through async/await. Run code within explicit context:

```javascript
const span = tracer.startSpan('background-job');
const ctx = trace.setSpan(context.active(), span);
context.with(ctx, async () => {
  await doWork(); // child spans inherit background-job as parent
  span.end();
});
```

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Import app before tracing.js | No spans | Use `--require ./tracing.js` flag |
| Missing `HttpInstrumentation` | Express spans missing | Express instrumentation requires HTTP — enable both |
| OTLP port mismatch | Protocol error | 4317 = gRPC, 4318 = HTTP. Match exporter to port |
| Dynamic span names | Cardinality explosion | Use `GET /users/:id` not `GET /users/12345` |
| `span.end()` never called | Span not exported, leak | Always `try/finally` |
| ESM with `--require` | Silent failure | Use `--import` for ESM, `--require` for CJS |
| Bundler tree-shakes OTEL | Missing instrumentation | Mark `@opentelemetry/*` as external |
| `context.active()` in raw callback | Wrong context | Use `context.with()` or `context.bind()` |
| Prisma without preview flag | No DB spans | Add `previewFeatures: ["tracing"]` to schema |
| Auto-instrumentations in prod | Overhead, noise | Use selective instrumentations |
