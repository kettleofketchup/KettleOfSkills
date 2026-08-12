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

### There is no per-conversation container

The most consequential property of this chart, and the one people assume their way past. Upstream's own
README:

> **one** shared instance where all agents are comingled on the same pod and PVC, with no built-in auth, RBAC
> for users, or tenant isolation.

and, listing what **OpenHands Enterprise** adds over it:

> **Isolated agent sandboxes** — each agent run gets its own container rather than every agent sharing the
> pod's filesystem.

So *automatic* per-run isolation is the licensed feature. There is no chart value, env var, or `RUNTIME`
setting that turns it on here — looking for one is wasted time.

**But you are not stuck with one backend.** The OSS lever is to run additional agent-servers and register them
in the UI's `Manage backends` dialog. On Kubernetes that means this chart hosts the *UI plus one* backend,
while further backends are separate pods — a second release, a Coder workspace, a VM, anything reachable that
runs `agent-canvas --backend-only --public` with a `LOCAL_BACKEND_API_KEY`. Each is a real isolation boundary
because it is a different pod with a different filesystem, and each can have its own Docker daemon, resources
and lifecycle. Two caveats: switching backends switches all settings/LLM/MCP config with it, and the API key
is the only authentication in front of a backend — so an in-cluster backend needs a NetworkPolicy, not just a
key.

What the pod actually runs (verified against agent-canvas built from OpenHands `v1.40.1`): a single container
with three processes under `tini` — `openhands-agent-server` on 18000, the automation `uvicorn` app on 18001,
and a Node static-server on 8000 that serves the UI *and* reverse-proxies `/api → 18000`,
`/api/automation → 18001`. Only 8000 is exposed. The frontend's own runtime-services-info describes the agent
server as the place where "tool calls (terminal, file_editor, browser, etc.) execute" — i.e. in that same
container.

Practical consequences:

- Conversations get their own directory under `~/workspace/`, keyed by conversation ID. That directory is the
  entire isolation boundary.
- Anything ambient is shared: processes, ports, installed packages, and any Docker daemon you add. One
  conversation can delete another's containers or saturate the pod's CPU.
- No Docker socket is needed or used. The image ships no `docker` CLI and no daemon.
- Giving the agent Docker means adding a daemon yourself (a DinD sidecar), and it will be **shared by every
  conversation** — which is a real design decision, not a detail.

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
namespaces — useful when the agent should deploy applications.

**This has nothing to do with sandboxing.** Upstream's example values list a namespace literally named
`agent-sandbox`, which reads as if OpenHands will run agents there. It will not — `rbac.namespaces` only
creates a RoleBinding to the built-in `admin` ClusterRole so the *agent* can `kubectl` into that namespace.
The agent still executes inside its own pod. Naming a namespace `agent-sandbox` buys no isolation whatsoever.

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
