# Traefik TLS Options & Advanced TLS

## TLS Options (Static Config)

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS12

    modern:
      minVersion: VersionTLS13

    intermediate:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
      curvePreferences:
        - CurveP521
        - CurveP384
```

## Kubernetes TLSOption CRD

```yaml
apiVersion: traefik.io/v1alpha1
kind: TLSOption
metadata:
  name: modern
spec:
  minVersion: VersionTLS13
  sniStrict: true
  alpnProtocols:
    - h2
    - http/1.1
```

Reference in IngressRoute:
```yaml
spec:
  tls:
    options:
      name: modern
      namespace: default
```

## Client Authentication (mTLS)

```yaml
tls:
  options:
    mtls:
      clientAuth:
        caFiles:
          - /certs/client-ca.crt
        clientAuthType: RequireAndVerifyClientCert
        # Options: NoClientCert, RequestClientCert,
        # RequireAnyClientCert, VerifyClientCertIfGiven,
        # RequireAndVerifyClientCert
```

## Router TLS Configuration

```yaml
http:
  routers:
    secure:
      rule: Host(`example.com`)
      tls:
        certResolver: letsencrypt
        options: modern
        domains:
          - main: example.com
            sans:
              - www.example.com
```

## IngressRoute TLS

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: secure-app
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`app.example.com`)
      kind: Rule
      services:
        - name: app
          port: 80
  tls:
    certResolver: letsencrypt
    # Or manual:
    # secretName: app-tls
    options:
      name: modern
    domains:
      - main: app.example.com
        sans:
          - api.example.com
```

## TCP TLS Passthrough

```yaml
tcp:
  routers:
    passthrough:
      rule: HostSNI(`db.example.com`)
      tls:
        passthrough: true
      service: database
```
