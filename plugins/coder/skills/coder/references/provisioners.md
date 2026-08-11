# Provisioners

Provisioner daemons run `terraform apply` for workspace builds. Built-in daemons run inside the `coderd` pod;
external daemons run anywhere and connect outbound.

## Why External

The built-in provisioner executes user-authored Terraform with the control plane's service account and
environment — including its database credentials. External provisioners isolate that blast radius, let you
place build credentials near the target infra, and keep heavy `terraform` runs off the API server.

Disable built-ins once external ones are healthy:

```bash
coder server --provisioner-daemons=0        # or CODER_PROVISIONER_DAEMONS=0
```

## Authentication

**Scoped keys (recommended)** — org-scoped, no user identity, survives staff turnover:

```bash
coder provisioner keys create k8s-key --org default
# optionally restrict which jobs it accepts:
coder provisioner keys create k8s-key --org default --tag environment=kubernetes
```

**User tokens** — the daemon inherits a Template Admin's identity; dies when that user leaves:

```bash
export CODER_SESSION_TOKEN=...
coder provisioner start --tag environment=kubernetes
```

**Global PSK** — one shared secret for the whole deployment. Not recommended: it cannot be scoped or rotated
per daemon.

## Tags

Every provisioner carries two automatic tags:

- `scope` = `organization` (with `owner=""`) or `user` (with `owner=<uuid>`)
- `owner` = user UUID for user-scoped daemons

Matching rule: a daemon runs a job only if **the job's tags are a subset of the daemon's tags**. A daemon with
no explicit tags accepts only untagged jobs.

```hcl
# In the template — route builds to a specific fleet
data "coder_workspace_tags" "tags" {
  tags = {
    environment = "kubernetes"
    region      = data.coder_parameter.region.value
  }
}
```

A template tagged `environment=kubernetes` will queue forever if no daemon advertises that tag. This is the
most common cause of a build that never starts — check `coder provisioner list` before debugging Terraform.

## External Provisioners on Kubernetes

```bash
kubectl create secret generic coder-provisioner-keys -n coder \
  --from-literal=k8s-key="<key from provisioner keys create>"
```

`provisioner-values.yaml`:

```yaml
coder:
  env:
    - name: CODER_URL
      value: "https://coder.example.com"
    - name: CODER_PROVISIONER_DAEMON_PSK   # omit when using keys
      value: ""
  replicaCount: 3
  resources:
    requests: { cpu: 500m, memory: 1Gi }
    limits:   { cpu: "2",  memory: 4Gi }
  serviceAccount:
    workspacePerms: true

provisionerDaemon:
  keySecretName: "coder-provisioner-keys"
  keySecretKey: "k8s-key"
```

```bash
helm install coder-provisioner coder-v2/coder-provisioner \
  -n coder -f provisioner-values.yaml --version <same as coderd>
```

Keep the provisioner chart version aligned with the `coderd` chart version.

`replicaCount` sets concurrency — each replica handles one build at a time. Size it to peak simultaneous
builds, not user count.

## Operations

```bash
coder provisioner list                     # daemons, tags, status, version
coder provisioner keys list --org default
coder provisioner keys delete <name> --org default
coder provisioner jobs list                # queued/running builds
coder provisioner jobs cancel <job-id>
```

## Metrics

```
CODER_PROMETHEUS_ENABLE=true
CODER_PROMETHEUS_ADDRESS=0.0.0.0:2112
```

Watch queue depth and job duration — a rising queue with idle daemons almost always means a tag mismatch
rather than insufficient capacity.

## Terraform Provider Caching

Provisioners run `terraform init` per build. In air-gapped or high-volume deployments, mount a filesystem
mirror and a persistent plugin cache into the provisioner pod:

```yaml
coder:
  env:
    - name: TF_PLUGIN_CACHE_DIR
      value: /home/coder/.terraform.d/plugin-cache
  volumes:
    - name: tf-cache
      persistentVolumeClaim: { claimName: tf-plugin-cache }
  volumeMounts:
    - name: tf-cache
      mountPath: /home/coder/.terraform.d/plugin-cache
```
