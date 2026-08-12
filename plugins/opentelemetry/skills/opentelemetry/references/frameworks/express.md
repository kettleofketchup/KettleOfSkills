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

See [express-advanced.md](express-advanced.md) for NestJS, Fastify, common Node.js patterns, and common mistakes.
