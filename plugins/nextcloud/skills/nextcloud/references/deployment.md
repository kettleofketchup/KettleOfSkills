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

```

See [helm-values-continued.md](helm-values-continued.md) for Redis, Storage, Cron, Probes, Resources, and Collabora CODE values.

See [traefik-ingressroute.md](traefik-ingressroute.md) for Traefik Middleware and IngressRoute manifests for Nextcloud and Collabora.

See [argocd-storage.md](argocd-storage.md) for ArgoCD Application manifests and Rook-Ceph StorageClass requirements.
