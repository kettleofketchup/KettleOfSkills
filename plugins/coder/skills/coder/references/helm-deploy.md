# Coder Helm & Kubernetes Deployment

## Install

```bash
helm repo add coder-v2 https://helm.coder.com/v2 && helm repo update
kubectl create namespace coder

# Mainline
helm install coder coder-v2/coder -n coder -f values.yaml --version 2.34.0
# Stable (OCI)
helm install coder oci://ghcr.io/coder/chart/coder -n coder -f values.yaml --version 2.33.6
```

## PostgreSQL

Required. The chart does NOT ship a production database — run CloudNativePG, an external managed instance, or
(dev only) the Bitnami subchart.

```bash
kubectl create secret generic coder-db-url -n coder \
  --from-literal=url="postgres://coder:PASSWORD@postgres.coder.svc.cluster.local:5432/coder?sslmode=require"
```

With CloudNativePG the cluster already publishes `<cluster>-app` holding `uri`; reference that key directly
rather than duplicating credentials.

## Chart Values Reference

| Key | Default | Purpose |
|-----|---------|---------|
| `coder.image.repo` | `ghcr.io/coder/coder` | Image (change for air-gap registry) |
| `coder.image.tag` | chart appVersion | Pin explicitly in prod |
| `coder.env` | `[]` | List of `name`/`value` or `valueFrom` — all `CODER_*` config lives here |
| `coder.replicaCount` | `1` | >1 requires Premium license |
| `coder.service.type` | `LoadBalancer` | Set `ClusterIP` when fronting with Traefik/ingress |
| `coder.service.enable` | `true` | Create Service |
| `coder.ingress.enable` | `false` | Chart-managed Ingress |
| `coder.tls.secretNames` | `[]` | TLS secrets mounted for coderd-terminated TLS |
| `coder.resources` | unset | Always set requests/limits |
| `coder.serviceAccount.workspacePerms` | `true` | Grants RBAC to manage workspace pods/PVCs |
| `coder.serviceAccount.enableDeployments` | `true` | Allows managing Deployments |
| `coder.securityContext.runAsUser` | `1000` | Container UID |
| `coder.podSecurityContext` | `{}` | fsGroup / runAs* |
| `coder.volumes` / `coder.volumeMounts` | `[]` | Extra mounts (CA bundles) |
| `provisionerDaemon.pskSecretName` | `""` | Pre-shared key (prefer scoped keys instead) |
| `extraTemplates` | — | Arbitrary extra manifests rendered with the release |

Full values: `helm show values coder-v2/coder`.

## Ingress with Traefik

Set `coder.service.type: ClusterIP`, disable the chart ingress, and route with an IngressRoute. Both the apex
and the wildcard host must resolve and be covered by the certificate.

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata: { name: coder, namespace: coder }
spec:
  entryPoints: [websecure]
  routes:
    - match: Host(`coder.example.com`) || HostRegexp(`^.+\.coder\.example\.com$`)
      kind: Rule
      services:
        - name: coder
          port: 80
  tls:
    secretName: coder-tls   # must be a wildcard cert: coder.example.com + *.coder.example.com
```

cert-manager DNS-01 is required for the wildcard — HTTP-01 cannot issue `*.` certificates.

## Workspace RBAC

The chart's service account provisions workspaces in its own namespace by default. To place workspaces in a
separate namespace, create a Role/RoleBinding there for the `coder` service account covering
`pods`, `persistentvolumeclaims`, `deployments`, `services`, `secrets`, and `events`, then set the template's
Kubernetes provider namespace accordingly.

Isolating workspaces in their own namespace is strongly preferred — it keeps user-authored Terraform away from
the control plane's secrets.

## Upgrades

```bash
helm repo update
helm upgrade coder coder-v2/coder -n coder -f values.yaml --version <target>
kubectl rollout status deploy/coder -n coder
```

Database migrations run automatically at startup and are not reversible. Snapshot PostgreSQL before upgrading.
Do not skip more than one minor version at a time. Running workspaces survive a control-plane restart; agents
reconnect once `coderd` is back.

## HA (Premium)

Set `coder.replicaCount: 3`. All replicas share the PostgreSQL instance and coordinate through it — no extra
config needed beyond the license. Ensure the LoadBalancer/ingress distributes across replicas and that
`CODER_ACCESS_URL` points at the shared address, not a pod.

## Air-Gapped

1. Mirror `ghcr.io/coder/coder`, the workspace base images, and any Terraform provider binaries.
2. Set `CODER_TELEMETRY_ENABLE=false`.
3. Provide a provider mirror so `terraform init` inside provisioners resolves offline:
   `CODER_PROVISIONER_DAEMON_...` env plus a `.terraformrc` with a `filesystem_mirror` block mounted into the
   provisioner pod.
4. Templates must reference internal registries only.

## Useful Server Env Vars

| Variable | Purpose |
|----------|---------|
| `CODER_ACCESS_URL` | External URL agents and CLI dial; must be reachable from workspaces |
| `CODER_WILDCARD_ACCESS_URL` | `*.coder.example.com` — enables subdomain app routing |
| `CODER_PG_CONNECTION_URL` | PostgreSQL DSN |
| `CODER_TELEMETRY_ENABLE` | `false` for air-gap/privacy |
| `CODER_PROMETHEUS_ENABLE` / `CODER_PROMETHEUS_ADDRESS` | Metrics (default `127.0.0.1:2112`) |
| `CODER_LOG_HUMAN` / `CODER_LOG_JSON` | Log destination/format |
| `CODER_DISABLE_PASSWORD_AUTH` | Force SSO-only login |
| `CODER_PROVISIONER_DAEMONS` | `0` disables built-in provisioners |
| `CODER_DERP_SERVER_ENABLE` | Built-in relay for workspace connectivity |
| `CODER_BROWSER_ONLY` | Premium; restrict to web access (no SSH) |
