# Helm Setup for Kubernetes

## Prerequisites

- Kubernetes cluster is set up.
- Helm is installed.

## Installation Steps

1. **Add Open WebUI Helm Repository:**

   ```bash
   helm repo add open-webui https://open-webui.github.io/helm-charts
   helm repo update
   ```

2. **Install Open WebUI Chart:**

   ```bash
   helm install openwebui open-webui/open-webui
   ```

3. **Verify Installation:**

   ```bash
   kubectl get pods
   ```

## Multi-Replica Warning

If you intend to scale Open WebUI using multiple nodes/pods/workers in a clustered environment, you need to setup a NoSQL key-value database (Redis). There are some environment variables that need to be set to the same value for all service-instances, otherwise consistency problems, faulty sessions and other issues will occur.

The default vector database (ChromaDB) uses a local SQLite-backed client that is not safe for multi-replica or multi-worker deployments. SQLite connections are not fork-safe, and concurrent writes from multiple processes will crash workers instantly. You must switch to an external vector database (PGVector, Milvus, Qdrant) via `VECTOR_DB`, or run ChromaDB as a separate HTTP server via `CHROMA_HTTP_HOST`.

## Critical for Updates

If you run Open WebUI with multiple replicas/pods (`replicaCount > 1`) or `UVICORN_WORKERS > 1`, you MUST scale down to a single replica/pod during updates:

1. Scale down deployment to 1 replica.
2. Apply the update (new image version).
3. Wait for the pod to be fully ready (database migrations complete).
4. Scale back up to your desired replica count.

Failure to do this can result in database corruption due to concurrent migrations.

## Access the WebUI

You can access Open WebUI by port-forwarding or configuring an Ingress.

### Ingress Configuration (Nginx)

If using the NGINX Ingress Controller, enable session affinity (sticky sessions) for WebSocket stability:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "open-webui-session"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
```

This ensures that a user's session remains connected to the same pod.

## Uninstall

1. **Uninstall the Helm Release:**
    ```bash
    helm uninstall openwebui
    ```

2. **Remove Persistent Volume Claims (deletes all data):**
    ```bash
    kubectl delete pvc -l app.kubernetes.io/instance=openwebui
    ```
