# Nextcloud Kubernetes Deployment

## Prerequisites

Create secrets before deploying:

```bash
NS=nextcloud
kubectl create ns $NS

# Nextcloud admin
kubectl create secret generic nextcloud-admin -n $NS \
  --from-literal=username=admin \
  --from-literal=password="$(openssl rand -base64 24)"

# PostgreSQL
kubectl create secret generic nextcloud-db -n $NS \
  --from-literal=postgres-password="$(openssl rand -base64 24)" \
  --from-literal=password="$(openssl rand -base64 24)"

# Redis
kubectl create secret generic nextcloud-redis -n $NS \
  --from-literal=redis-password="$(openssl rand -base64 24)"

# Collabora admin (optional)
kubectl create secret generic collabora-admin -n $NS \
  --from-literal=username=admin \
  --from-literal=password="$(openssl rand -base64 24)"
```

## Helm Values Template

```yaml
image:
  flavor: apache  # or fpm (requires nginx sidecar)

replicaCount: 1
strategy:
  type: Recreate  # required for RWO volumes

nextcloud:
  host: cloud.example.com
  existingSecret:
    enabled: true
    secretName: nextcloud-admin
    usernameKey: username
    passwordKey: password
  trustedDomains:
    - cloud.example.com
    - nextcloud.nextcloud.svc.cluster.local
  configs:
    proxy.config.php: |-
      <?php
      $CONFIG = array (
        'trusted_proxies' => array(
          0 => '127.0.0.1',
          1 => '10.244.0.0/16',
          2 => '192.168.5.0/24',
        ),
        'forwarded_for_headers' => array('HTTP_X_FORWARDED_FOR'),
      );
    custom.config.php: |-
      <?php
      $CONFIG = array (
        'default_phone_region' => 'US',
        'maintenance_window_start' => 1,
        'filelocking.enabled' => true,
      );
  phpConfigs:
    zz-custom.ini: |-
      memory_limit=512M
      upload_max_filesize=16G
      post_max_size=16G
      max_execution_time=3600
      max_input_time=3600

phpClientHttpsFix:
  enabled: true
  protocol: https

# --- Database ---
internalDatabase:
  enabled: false

postgresql:
  enabled: true
  global:
    postgresql:
      auth:
        username: nextcloud
        database: nextcloud
        existingSecret: nextcloud-db
        secretKeys:
          adminPasswordKey: postgres-password
          userPasswordKey: password
  primary:
    persistence:
      enabled: true
      storageClass: "ceph-block"
      size: 8Gi

# --- Cache ---
redis:
  enabled: true
  auth:
    enabled: true
    existingSecret: nextcloud-redis
    existingSecretPasswordKey: redis-password
  master:
    persistence:
      enabled: true
      storageClass: "ceph-block"
      size: 2Gi
  replica:
    replicaCount: 0  # single replica for homelab

# --- Storage ---
persistence:
  enabled: true
  storageClass: "ceph-block"
  accessMode: ReadWriteOnce
  size: 8Gi
  nextcloudData:
    enabled: true
    storageClass: "ceph-block"  # RWO for single replica
    accessMode: ReadWriteOnce
    size: 50Gi

# --- Cron ---
cronjob:
  enabled: true
  # sidecar runs cron.sh in same pod (shares volumes)

# --- Ingress (disable if using IngressRoute) ---
ingress:
  enabled: false

# --- Probes ---
startupProbe:
  enabled: true
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 30  # 5 min total for first boot
livenessProbe:
  enabled: true
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  enabled: true
  initialDelaySeconds: 10
  periodSeconds: 10

# --- Resources ---
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi

# --- Collabora CODE (optional) ---
collabora:
  enabled: true
  collabora:
    aliasgroups:
      - host: "https://cloud.example.com"
    extra_params: "--o:ssl.enable=false"
    server_name: collabora.example.com
    existingSecret:
      enabled: true
      secretName: collabora-admin
      usernameKey: username
      passwordKey: password
  ingress:
    enabled: false  # use IngressRoute instead
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
```

## Traefik IngressRoute

Create separately or via `extraManifests` in values:

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

## ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nextcloud
  namespace: argocd
spec:
  project: default
  source:
    chart: nextcloud
    repoURL: https://nextcloud.github.io/helm/
    targetRevision: "8.*"
    helm:
      valueFiles:
        - values.yaml  # from git repo
  destination:
    server: https://kubernetes.default.svc
    namespace: nextcloud
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

For app-of-apps pattern, place values.yaml in the git repo and reference via multi-source:

```yaml
spec:
  sources:
    - repoURL: https://nextcloud.github.io/helm/
      chart: nextcloud
      targetRevision: "8.*"
      helm:
        valueFiles:
          - $values/nextcloud/values.yaml
    - repoURL: git@github.com:kettleofketchup/home.git
      targetRevision: main
      ref: values
```

## Storage Classes (Rook-Ceph)

Ensure these StorageClasses exist:

| StorageClass | Provisioner | Access | Use |
|-------------|-------------|--------|-----|
| `ceph-block` | rook-ceph.rbd.csi.ceph.com | RWO | PostgreSQL, Redis, Nextcloud app |
| `ceph-filesystem` | rook-ceph.cephfs.csi.ceph.com | RWX | Multi-replica data (if needed) |

Single-replica deployment: use `ceph-block` (RWO) for everything — simpler and better performance.
Multi-replica: `ceph-filesystem` (RWX) for nextcloudData, sticky sessions required.
