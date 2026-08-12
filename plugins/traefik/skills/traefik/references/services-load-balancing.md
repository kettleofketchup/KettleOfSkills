# Traefik Services & Load Balancing

## Basic Service Configuration

```yaml
http:
  services:
    my-service:
      loadBalancer:
        servers:
          - url: http://backend1:8080
          - url: http://backend2:8080
        passHostHeader: true
```

## Load Balancing Strategies

| Strategy | Description |
|----------|-------------|
| `wrr` | Weighted Round Robin (default) |
| `p2c` | Power of Two Choices - picks server with fewer connections |
| `hrw` | Highest Random Weight - consistent hashing by client IP |
| `leasttime` | Lowest response time + fewest connections |

```yaml
http:
  services:
    my-service:
      loadBalancer:
        strategy: p2c
        servers:
          - url: http://backend1:8080
          - url: http://backend2:8080
```

## Weighted Servers

```yaml
http:
  services:
    weighted:
      loadBalancer:
        servers:
          - url: http://backend1:8080
            weight: 3  # 75% traffic
          - url: http://backend2:8080
            weight: 1  # 25% traffic
```

## Health Checks

### Active Health Check

```yaml
http:
  services:
    my-service:
      loadBalancer:
        servers:
          - url: http://backend:8080
        healthCheck:
          path: /health
          interval: 10s
          timeout: 3s
          scheme: http
          port: 8080
          hostname: backend.local
          method: GET
          status: 200
          headers:
            X-Health-Check: "true"
```

### Passive Health Check

```yaml
http:
  services:
    my-service:
      loadBalancer:
        servers:
          - url: http://backend:8080
        passiveHealthCheck:
          failureWindow: 10s
          maxFailedAttempts: 3
```

## Sticky Sessions

```yaml
http:
  services:
    sticky-service:
      loadBalancer:
        servers:
          - url: http://backend1:8080
          - url: http://backend2:8080
        sticky:
          cookie:
            name: my-sticky-cookie
            maxAge: 3600        # Seconds (0 = session cookie)
            secure: true
            httpOnly: true
            sameSite: strict    # strict, lax, none
            domain: .example.com
```

## Response Forwarding

```yaml
http:
  services:
    my-service:
      loadBalancer:
        servers:
          - url: http://backend:8080
        responseForwarding:
          flushInterval: 100ms  # For streaming responses
```

## ServersTransport (Backend TLS)

```yaml
http:
  serversTransports:
    secure-transport:
      serverName: backend.internal
      insecureSkipVerify: false
      rootCAs:
        - /certs/ca.crt
      certificates:
        - certFile: /certs/client.crt
          keyFile: /certs/client.key
      maxIdleConnsPerHost: 100
      forwardingTimeouts:
        dialTimeout: 30s
        responseHeaderTimeout: 30s
        idleConnTimeout: 90s

  services:
    secure-service:
      loadBalancer:
        serversTransport: secure-transport
        servers:
          - url: https://backend:8443
```
