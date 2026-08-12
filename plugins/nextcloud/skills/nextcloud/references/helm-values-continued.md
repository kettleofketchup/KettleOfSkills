# Nextcloud Helm Values (continued)

Continuation of `deployment.md` Helm values template — Redis, Storage, Cron, Probes, Resources, and Collabora CODE.

```yaml
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
