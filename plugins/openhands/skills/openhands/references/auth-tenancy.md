# Authentication & Multi-Tenancy

## The Baseline

The OSS OpenHands server has **no user accounts, no login, and no authorization**. Whoever reaches the port
gets the agent, the configured LLM key, the stored git tokens, and a shell in the sandbox — which, in the
default Docker deployment, holds the host's docker socket.

Bind to localhost (`-p 127.0.0.1:3000:3000`) or put an authenticating proxy in front. There is no third
option that is safe.

## Single-User Behind Authentik (Recommended OSS Path)

Traefik forward-auth to Authentik in front of one OpenHands instance.

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata: { name: authentik-forward-auth, namespace: authentik }
spec:
  forwardAuth:
    address: http://authentik-server.authentik.svc.cluster.local:80/outpost.goauthentik.io/auth/traefik
    trustForwardHeader: true
    authResponseHeaders:
      - X-authentik-username
      - X-authentik-groups
      - X-authentik-email
      - X-authentik-uid
```

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
        - name: authentik-forward-auth
          namespace: authentik
      services:
        - name: openhands
          port: 8000
  tls: { secretName: openhands-tls }
```

On the Authentik side create a **Proxy Provider** (forward auth, single application) plus an Application bound
to the group allowed in. See the `authentik` skill's forward-auth references.

This authenticates the *route*, not the application. Everyone who passes shares one identity inside OpenHands:
same settings, same secrets, same history. It is correct for one user or a trusted pair — not for a team.

## Per-User Instances (OSS Multi-User)

Real isolation without the enterprise chart means one release per user.

```bash
helm install openhands-alice ./OpenHands/helm/agent-canvas \
  -n openhands-alice --create-namespace \
  --set ingress.host=alice.openhands.example.com \
  -f alice-values.yaml
```

Per user: own namespace, own PVC, own LLM virtual key, own Authentik policy binding the route to that person
only.

| Aspect | Result |
|--------|--------|
| Data isolation | Full — separate PVCs |
| Credential isolation | Full — separate secrets and virtual keys |
| Cost attribution | Per LiteLLM virtual key |
| Overhead | One StatefulSet + PVC per user |
| Management | Templatable with ArgoCD ApplicationSet over a user list |

An ApplicationSet with a list generator over usernames makes this maintainable — adding a user is a one-line
commit. It is the honest OSS answer to "multi-user"; the alternative is the licensed platform.

## Enterprise Multi-Tenancy

The enterprise chart ships real tenancy: **Keycloak** for identity, a **Runtime API** issuing per-user
sandboxes in a dedicated namespace, LiteLLM for per-user keys and budgets, PostgreSQL for shared state.

Authentik integrates by federating into Keycloak as an external OIDC identity provider, rather than replacing
it — the chart expects Keycloak. In Keycloak: Identity Providers → OpenID Connect v1.0, pointed at
`https://auth.example.com/application/o/<slug>/`, with a mapper carrying groups through.

Chart-required Keycloak secrets: `keycloak-admin` (admin-password) and `keycloak-realm` (realm-name,
server-url, client-id, client-secret, smtp-password). → `helm-k8s.md`

Git provider auth is separate: the chart wants a GitHub App (`github-app` secret with app-id, app-slug,
client-id, client-secret, private-key, webhook-secret), or GitLab/Bitbucket Data Center equivalents.

## Secrets Handling

| Secret | Where it belongs |
|--------|------------------|
| LLM keys | Kubernetes Secret → `extraEnv`, or a LiteLLM virtual key |
| Git tokens | OpenHands Settings → Secrets, or `SANDBOX_ENV_*` |
| Arbitrary sandbox env | `SANDBOX_ENV_<NAME>` — forwarded into the sandbox only |

`SANDBOX_ENV_*` exists so the sandbox gets exactly the credentials it needs, rather than inheriting the
server's environment. Use it instead of exporting keys globally.

Anything reachable from the sandbox is reachable by model-generated code. Don't mount kubeconfigs, cloud
credential files, or the host SSH agent into a sandbox.

## Hardening Checklist

- [ ] Never publish the port without forward-auth or localhost binding
- [ ] `RUNTIME=docker` (never `process` on a shared or credentialed host)
- [ ] `SECURITY_CONFIRMATION_MODE=true` when the sandbox touches anything irreplaceable
- [ ] `MAX_BUDGET_PER_TASK` and `MAX_ITERATIONS` set
- [ ] Sandbox namespace: ResourceQuota, LimitRange, egress NetworkPolicy
- [ ] No service account token automounting in the sandbox namespace
- [ ] `SANDBOX_VOLUMES` scoped to project dirs, never `$HOME`
- [ ] LLM access via gateway virtual keys with hard budget caps
- [ ] Pinned image tags for server and agent-server
- [ ] `JWT_SECRET` pinned so sessions survive restarts
- [ ] gVisor/Sysbox runtime class where kernel isolation matters

## Sandbox Egress Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: sandbox-egress, namespace: openhands-runtimes }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: litellm }
      ports: [{ protocol: TCP, port: 4000 }]
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
    # add explicit egress for package registries and git as needed
```

Agents legitimately need `pip`/`npm`/`git` reachable, so a deny-all policy breaks normal work. Allow the
registries you use by name and keep everything else closed — particularly the cluster's internal services and
cloud metadata endpoints (`169.254.169.254`).
