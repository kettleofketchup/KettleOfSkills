# OpenHands on Kubernetes

Two distinct charts. The OSS one is a single-tenant app; the enterprise one is a multi-tenant platform.

## OSS: agent-canvas Chart

Source: `helm/agent-canvas/` in `github.com/OpenHands/OpenHands`. Deploys the all-in-one image (frontend +
agent-server + automation) as a **StatefulSet** with a PVC, Service, optional Ingress and RBAC.

```bash
git clone https://github.com/OpenHands/OpenHands.git
helm install openhands ./OpenHands/helm/agent-canvas -n openhands --create-namespace -f values.yaml
```

### Values

```yaml
image:
  repository: ghcr.io/openhands/agent-canvas
  tag: ""                    # defaults to chart appVersion — pin explicitly
  pullPolicy: IfNotPresent

persistence:
  enabled: true
  size: 20Gi
  accessModes: [ReadWriteOnce]
  storageClassName: ""       # cluster default

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: false
  host: agent-canvas.local

config:
  port: 8000
  agentServerPort: 18000
  automationPort: 18001
  automationDbUrl: ""        # empty → SQLite on the PVC
  extraEnv: []

rbac:
  enabled: false
  namespaces: []
  clusterAdmin: false

resources:
  requests: { cpu: 500m, memory: 1Gi }
  limits:   { cpu: "2",  memory: 4Gi }

securityContext:
  fsGroup: 10001
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001

serviceAccount:
  create: true
  automountServiceAccountToken: true
```

### Storage Layout

The single PVC is mounted at two subPaths:

- `~/.openhands` — settings, secrets, conversation history, automation DB
- `~/workspace` — cloned repos and generated files

`fsGroup: 10001` is what lets the container (UID 10001) write to the volume. Overriding
`securityContext` without preserving it produces a pod that starts and then fails every write.

`ReadWriteOnce` + StatefulSet means **one replica**. This chart does not scale horizontally.

### Credentials

Don't type keys into the UI on a shared cluster — inject them:

```bash
kubectl create secret generic openhands-llm -n openhands \
  --from-literal=api-key='sk-...'
```

```yaml
config:
  extraEnv:
    - name: LLM_API_KEY
      valueFrom: { secretKeyRef: { name: openhands-llm, key: api-key } }
    - name: LLM_MODEL
      value: "litellm_proxy/claude-sonnet-4-5"
    - name: LLM_BASE_URL
      value: "http://litellm.litellm.svc.cluster.local:4000"
    - name: MAX_BUDGET_PER_TASK
      value: "5.0"
```

### RBAC

Disabled by default. Enabling grants the pod's service account rights to run `kubectl` against listed
namespaces — useful when the agent should deploy applications:

```yaml
rbac:
  enabled: true
  namespaces: [dev-apps]
  clusterAdmin: false
```

`clusterAdmin: true` gives an LLM-driven agent cluster-admin. There is no scenario on a shared cluster where
that's the right call; scope to namespaces instead.

### Ingress with Traefik

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata: { name: openhands, namespace: openhands }
spec:
  entryPoints: [websecure]
  routes:
    - match: Host(`openhands.example.com`)
      kind: Rule
      middlewares:
        - name: authentik-forward-auth      # OSS has no auth of its own
          namespace: authentik
      services:
        - name: openhands
          port: 8000
  tls: { secretName: openhands-tls }
```

The forward-auth middleware is not optional — see `auth-tenancy.md`.

Enterprise/multi-tenant chart: → `helm-enterprise.md`
