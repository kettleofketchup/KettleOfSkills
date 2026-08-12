---
description: Raw Kubernetes manifests for Foundry VTT: Namespace, Secret, PVC, Deployment, Service
last_updated: 2026-03-18
---

# Foundry VTT Kubernetes Manifests

## Namespace + Secret

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

## PersistentVolumeClaim

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

## Deployment

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

## Service

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
