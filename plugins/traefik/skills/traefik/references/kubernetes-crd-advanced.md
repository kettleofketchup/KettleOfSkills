# Traefik Kubernetes CRDs - Advanced (TraefikService, TLSOption, Provider)

## TraefikService - Weighted Round Robin

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: weighted-service
spec:
  weighted:
    services:
      - name: app-v1
        port: 80
        weight: 80
      - name: app-v2
        port: 80
        weight: 20
```

## TraefikService - Mirroring

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: mirror-service
spec:
  mirroring:
    name: main-service
    port: 80
    mirrors:
      - name: test-service
        port: 80
        percent: 10
```

## TraefikService - Failover

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: failover-service
spec:
  failover:
    service:
      name: primary-service
      port: 80
    fallback:
      name: backup-service
      port: 80
```

## TLSOption

```yaml
apiVersion: traefik.io/v1alpha1
kind: TLSOption
metadata:
  name: modern-tls
spec:
  minVersion: VersionTLS12
  cipherSuites:
    - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
  curvePreferences:
    - CurveP521
    - CurveP384
  sniStrict: true
```

## Provider Configuration (Static Config)

```yaml
providers:
  kubernetesCRD:
    namespaces:
      - default
      - production
    allowCrossNamespace: true
    allowEmptyServices: false
    labelselector: "app=traefik-managed"
```

| Option | Description | Default |
|--------|-------------|---------|
| `namespaces` | Watch specific namespaces (empty = all) | [] |
| `allowCrossNamespace` | Allow cross-namespace references | false |
| `allowEmptyServices` | Route to services with no endpoints | false |
| `labelselector` | Filter resources by label | "" |
| `ingressClass` | Filter by annotation value | "" |
