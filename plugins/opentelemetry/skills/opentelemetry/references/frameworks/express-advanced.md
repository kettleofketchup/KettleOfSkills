---
last_updated: 2026-03-08
---

# Node.js OTEL: NestJS, Fastify, Patterns, and Mistakes

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
const { FastifyOtelInstrumentation } = require('@fastify/otel');
const fastifyOtel = new FastifyOtelInstrumentation({ servername: 'my-fastify-api' });
instrumentations: [new HttpInstrumentation(), fastifyOtel],
await app.register(fastifyOtel.plugin());
app.get('/health', (req) => {
  const { span } = req.openTelemetry();
  span.setAttribute('health.status', 'ok');
  return { status: 'ok' };
});
```

## Common Node.js Patterns

### diagnostics_channel

`@opentelemetry/instrumentation-undici` traces `fetch()` and undici automatically:

```javascript
instrumentations: [new UndiciInstrumentation(), new HttpInstrumentation()],
```

### Database Tracing

| ORM/Driver | Package | Notes |
|-----------|---------|-------|
| Prisma | `@prisma/instrumentation` | Also add `previewFeatures: ["tracing"]` in schema.prisma |
| TypeORM | Auto-detected | Via underlying pg/mysql driver instrumentation |
| Knex | `@opentelemetry/instrumentation-knex` | Query builder operation spans |
| pg | `@opentelemetry/instrumentation-pg` | Raw query spans with parameters |
| Mongoose | `@opentelemetry/instrumentation-mongoose` | MongoDB operation spans |

### Context Propagation (AsyncLocalStorage)

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
