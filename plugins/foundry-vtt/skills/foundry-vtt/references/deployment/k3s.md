---
description: Foundry VTT on Kubernetes/K3s, Helm charts, PVC, Traefik ingress with WebSocket, manifests
last_updated: 2026-03-18
---

# Foundry VTT on K3s/Kubernetes

## Helm Charts

### Hugo Prudente Chart (recommended)

```bash
helm repo add foundry-vtt https://hugoprudente.github.io/helm-charts/incubator/
helm repo update
helm install foundry foundry-vtt/foundry-vtt --values values.yaml
```

Available on ArtifactHub: `hugoprudente/foundry-vtt` (supports up to v12.x+).

### k8s-at-home Chart (legacy)

```bash
helm repo add k8s-at-home https://k8s-at-home.com/charts/
helm install foundry k8s-at-home/foundryvtt --values values.yaml
```

## Raw Kubernetes Manifests

### Namespace + Secret

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: foundry
---
apiVersion: v1
kind: Secret
metadata:
  name: foundry-credentials
  namespace: foundry
type: Opaque
stringData:
  FOUNDRY_USERNAME: "your-email@example.com"
  FOUNDRY_PASSWORD: "your-password"
  FOUNDRY_ADMIN_KEY: "your-admin-key"
```

### PersistentVolumeClaim

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: foundry-data
  namespace: foundry
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: local-path    # K3s default, or ceph-block
  resources:
    requests:
      storage: 20Gi              # Adjust for assets (maps, tokens)
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: foundry
  namespace: foundry
spec:
  replicas: 1                    # Single instance only (license restriction)
  selector:
    matchLabels:
      app: foundry
  template:
    metadata:
      labels:
        app: foundry
    spec:
      containers:
        - name: foundry
          image: felddy/foundryvtt:13
          ports:
            - containerPort: 30000
          envFrom:
            - secretRef:
                name: foundry-credentials
          env:
            - name: FOUNDRY_PROXY_SSL
              value: "true"
            - name: FOUNDRY_PROXY_PORT
              value: "443"
            - name: FOUNDRY_HOSTNAME
              value: "foundry.example.com"
            - name: CONTAINER_PRESERVE_CONFIG
              value: "true"
          volumeMounts:
            - name: data
              mountPath: /data
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: "2"
              memory: 2Gi
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: foundry-data
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: foundry
  namespace: foundry
spec:
  selector:
    app: foundry
  ports:
    - port: 30000
      targetPort: 30000
```

## Traefik IngressRoute (WebSocket Required)

Foundry VTT requires WebSocket support. Traefik handles this natively:

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: foundry
  namespace: foundry
spec:
  entryPoints: [websecure]
  routes:
    - match: Host(`foundry.example.com`)
      kind: Rule
      services:
        - name: foundry
          port: 30000
  tls:
    certResolver: letsencrypt    # or secretName for cert-manager
```

Traefik passes WebSocket connections by default (no extra middleware needed).

### Nginx Ingress Alternative

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: foundry
  namespace: foundry
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
spec:
  rules:
    - host: foundry.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: foundry
                port:
                  number: 30000
  tls:
    - hosts: [foundry.example.com]
      secretName: foundry-tls
```

## Resource Recommendations

| Workload | CPU | Memory | Storage |
|----------|-----|--------|---------|
| Light (1-4 players) | 250m-500m | 512Mi-1Gi | 10Gi |
| Medium (5-8 players) | 500m-1000m | 1Gi-2Gi | 20Gi |
| Heavy (modules+assets) | 1000m-2000m | 2Gi-4Gi | 50Gi+ |

Storage grows with: uploaded maps, token art, music, compendium data.

## Backup & Upgrade

Back up PVC `/data` before upgrades. Critical: `/data/Data/worlds/` (saves), `/data/Config/options.json` (config). Modules/systems are reinstallable.

Upgrade: change image tag, Foundry auto-migrates world data. Verify module compatibility first.
