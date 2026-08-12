# Nextcloud Traefik IngressRoute

Create separately or via `extraManifests` in Helm values:

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: nextcloud-headers
  namespace: nextcloud
spec:
  headers:
    stsSeconds: 15768000
    stsIncludeSubdomains: true
    customResponseHeaders:
      X-Robots-Tag: "noindex, nofollow"
---
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: nextcloud
  namespace: nextcloud
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`cloud.example.com`)
      kind: Rule
      services:
        - name: nextcloud
          port: 8080
      middlewares:
        - name: nextcloud-headers
  tls:
    secretName: nextcloud-tls
---
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: collabora
  namespace: nextcloud
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`collabora.example.com`)
      kind: Rule
      services:
        - name: nextcloud-collabora
          port: 9980
  tls:
    secretName: collabora-tls
```
