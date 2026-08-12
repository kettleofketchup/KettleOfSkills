# Traefik Middlewares - Traffic Control & Headers

## RateLimit

```yaml
http:
  middlewares:
    ratelimit:
      rateLimit:
        average: 100      # Requests per period
        burst: 50         # Max concurrent
        period: 1m        # Time period
        sourceCriterion:
          requestHost: true  # Group by host
          # Or by header:
          # requestHeaderName: X-API-Key
          # Or by IP:
          # ipStrategy:
          #   depth: 1
```

## Headers

```yaml
http:
  middlewares:
    security:
      headers:
        # Security headers
        frameDeny: true
        browserXssFilter: true
        contentTypeNosniff: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true

        # Custom headers
        customRequestHeaders:
          X-Custom: "value"
        customResponseHeaders:
          X-Response: "value"

        # CORS
        accessControlAllowOriginList:
          - "https://example.com"
        accessControlAllowMethods:
          - GET
          - POST
        accessControlAllowHeaders:
          - Authorization
        accessControlMaxAge: 100
```

## StripPrefix

```yaml
http:
  middlewares:
    strip:
      stripPrefix:
        prefixes:
          - /api
          - /v1
```

Request `/api/users` → Backend sees `/users`. Sets `X-Forwarded-Prefix: /api` header.

## RedirectScheme

```yaml
http:
  middlewares:
    https-redirect:
      redirectScheme:
        scheme: https
        permanent: true  # 301 vs 302
        port: "443"
```

## RedirectRegex

```yaml
http:
  middlewares:
    redirect:
      redirectRegex:
        regex: "^https://example.com/(.*)"
        replacement: "https://www.example.com/${1}"
        permanent: true
```

## CircuitBreaker

```yaml
http:
  middlewares:
    circuit:
      circuitBreaker:
        expression: NetworkErrorRatio() > 0.30 || ResponseCodeRatio(500, 600, 0, 600) > 0.25
        checkPeriod: 10s
        fallbackDuration: 30s
        recoveryDuration: 60s
```

## Retry

```yaml
http:
  middlewares:
    retry:
      retry:
        attempts: 3
        initialInterval: 100ms
```

## Compress

```yaml
http:
  middlewares:
    compress:
      compress:
        excludedContentTypes:
          - text/event-stream
        minResponseBodyBytes: 1024
```

## InFlightReq / Errors

```yaml
http:
  middlewares:
    inflight:
      inFlightReq:
        amount: 100
        sourceCriterion:
          requestHost: true
    errors:
      errors:
        status: [500-599]
        service: error-service
        query: /{status}.html
```
