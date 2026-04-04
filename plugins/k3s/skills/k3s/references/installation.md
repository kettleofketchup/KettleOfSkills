# K3s Installation & Configuration

## Install Methods

### Script Install (online)

```bash
curl -sfL https://get.k3s.io | sh -
```

Control behavior via environment variables:

| Variable | Purpose |
|----------|---------|
| `INSTALL_K3S_EXEC` | Override command (e.g., `server`, `agent`) |
| `INSTALL_K3S_VERSION` | Pin K3s version |
| `INSTALL_K3S_CHANNEL` | Release channel (stable, latest, testing) |
| `INSTALL_K3S_SKIP_DOWNLOAD` | Use pre-placed binary (airgap) |
| `INSTALL_K3S_SKIP_ENABLE` | Install but don't enable/start service |
| `INSTALL_K3S_SKIP_START` | Install+enable but don't start |
| `K3S_TOKEN` | Cluster join token |
| `K3S_URL` | Server URL for agent joining |
| `K3S_KUBECONFIG_MODE` | Kubeconfig permissions |
| `K3S_NODE_NAME` | Override node hostname |

### Binary Install (manual)

```bash
curl -Lo /usr/local/bin/k3s https://github.com/k3s-io/k3s/releases/download/VERSION/k3s
chmod +x /usr/local/bin/k3s

# Run directly
k3s server --cluster-init

# Or create systemd unit
k3s server --write-kubeconfig-mode=0644
```

### NixOS Module

Reference the `nixos` skill. K3s NixOS module uses `services.k3s`:

```nix
services.k3s = {
  enable = true;
  role = "server";
  extraFlags = [
    "--flannel-backend=none"
    "--disable-network-policy"
    "--disable=traefik"
  ];
};
```

## Configuration File

**Location:** `/etc/rancher/k3s/config.yaml`
**Drop-ins:** `/etc/rancher/k3s/config.yaml.d/*.yaml` (merged in alphabetical order)

CLI flags map directly to YAML keys. Repeatable flags become lists:

```yaml
write-kubeconfig-mode: "0644"
flannel-backend: "none"
disable-network-policy: true
disable:
  - traefik
  - servicelb
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
tls-san:
  - "k3s.example.com"
  - "10.0.0.100"
node-label:
  - "node-role.kubernetes.io/worker="
  - "topology.kubernetes.io/zone=edge-1"
kubelet-arg:
  - "max-pods=250"
kube-apiserver-arg:
  - "enable-admission-plugins=NodeRestriction"
```

### Drop-in Append Mode

Use `+` suffix to append rather than replace values across config files:

```yaml
# /etc/rancher/k3s/config.yaml.d/calico.yaml
disable+:
  - traefik
node-label+:
  - "cni=calico"
```

## Server vs Agent Flags

**Server-only flags** (must match across all servers in HA):
- `--cluster-cidr`, `--service-cidr`, `--cluster-dns`, `--cluster-domain`
- `--flannel-backend`, `--disable-network-policy`
- `--disable`, `--disable-helm-controller`
- `--secrets-encryption`
- `--cluster-init`, `--datastore-endpoint`

**Agent flags** (per-node):
- `--node-name`, `--node-label`, `--node-taint`
- `--kubelet-arg`, `--container-runtime-endpoint`
- `--flannel-iface` (which interface flannel uses)

## Component Management

Disable bundled components with `--disable`:

| Component | Description |
|-----------|-------------|
| `traefik` | Ingress controller |
| `servicelb` | Built-in LoadBalancer (Klipper) |
| `local-storage` | Local path provisioner |
| `coredns` | DNS (replace with custom) |
| `metrics-server` | Metrics API |

## Auto-Deploy Manifests

Files in `/var/lib/rancher/k3s/server/manifests/` auto-apply on K3s start. Supports `.yaml` and `.yml`. Changes to files trigger re-apply.

HelmChart CRD enables Helm installs via manifests:

```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: traefik
  namespace: kube-system
spec:
  chart: traefik
  repo: https://traefik.github.io/charts
  targetNamespace: traefik
  valuesContent: |-
    ports:
      web:
        exposedPort: 80
```
