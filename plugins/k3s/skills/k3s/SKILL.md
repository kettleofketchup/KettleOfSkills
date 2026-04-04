---
name: k3s
description: "Self-hosted K3s lightweight Kubernetes distribution. This skill should be used when installing or configuring K3s clusters, setting up server/agent nodes, configuring HA with embedded etcd, disabling default components (traefik, servicelb, flannel), replacing Flannel with custom CNI (Calico/tigera-operator, Cilium), configuring private registries (registries.yaml), deploying in airgapped/air-gapped environments (image pre-loading, INSTALL_K3S_SKIP_DOWNLOAD), managing K3s server flags (--cluster-cidr, --service-cidr, --flannel-backend=none, --disable-network-policy), writing /etc/rancher/k3s/config.yaml, troubleshooting containerd/kubelet issues, or integrating K3s with NixOS modules. Covers single-node and multi-node topologies."
---

# K3s - Lightweight Kubernetes

K3s is a CNCF-certified Kubernetes distribution built for edge, IoT, and resource-constrained environments. Single binary (~70MB), embeds containerd, SQLite (single-node) or etcd (HA).

## Key Paths

| Path | Purpose |
|------|---------|
| `/etc/rancher/k3s/config.yaml` | Server/agent configuration |
| `/etc/rancher/k3s/config.yaml.d/*.yaml` | Drop-in config fragments |
| `/etc/rancher/k3s/registries.yaml` | Private registry mirrors + auth |
| `/etc/rancher/k3s/k3s.yaml` | Kubeconfig (default mode 0600) |
| `/var/lib/rancher/k3s/` | K3s state directory |
| `/var/lib/rancher/k3s/agent/images/` | Airgap image tarballs |
| `/var/lib/rancher/k3s/agent/containerd/` | Containerd runtime data |
| `/var/lib/rancher/k3s/server/manifests/` | Auto-deploy manifests |

## Quick Reference

### Installation

```bash
# Standard install
curl -sfL https://get.k3s.io | sh -

# With options
curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET sh -s - server \
    --cluster-init --write-kubeconfig-mode=0644 --disable=traefik

# Agent join
curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET K3S_URL=https://server:6443 sh -

# Airgap (binary pre-placed)
INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh
```

### Common Server Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--flannel-backend` | `vxlan` | Set to `none` for custom CNI |
| `--disable` | — | Skip bundled components (traefik, servicelb, local-storage) |
| `--disable-network-policy` | false | Required when using external CNI |
| `--cluster-cidr` | `10.42.0.0/16` | Pod network CIDR |
| `--service-cidr` | `10.43.0.0/16` | Service network CIDR |
| `--cluster-init` | false | Enable embedded etcd for HA |
| `--write-kubeconfig-mode` | `0600` | Kubeconfig file permissions |
| `--data-dir` | `/var/lib/rancher/k3s` | State directory |
| `--tls-san` | — | Additional SANs for API server cert |

### Custom CNI (Calico/Cilium)

Disable Flannel and built-in network policy to use external CNI:

```yaml
# /etc/rancher/k3s/config.yaml
flannel-backend: "none"
disable-network-policy: true
disable:
  - traefik
  - servicelb
```

Then deploy Calico via tigera-operator Helm chart. See `references/networking.md`.

## Reference Files

| File | Content |
|------|---------|
| `references/installation.md` | Install methods, config file format, server/agent flags, environment variables |
| `references/airgap.md` | Airgap deployment patterns, image pre-loading, offline install, upgrades |
| `references/networking.md` | Flannel backends, custom CNI enablement, Calico/tigera setup, dual-stack |
| `references/registries.md` | Private registry mirrors, TLS, auth, registries.yaml format |
| `references/ha-etcd.md` | HA embedded etcd, cluster init, node joining, backup/restore |
| `references/troubleshooting.md` | Diagnostics, common issues, containerd/kubelet debugging |

## Cross-References

- **NixOS integration**: Use `nixos` skill for K3s NixOS modules, flake composition, airgap image bundling with Nix
- **Storage**: Use `rook-ceph` or `rook-ceph-single` skill for Ceph block storage on K3s
- **Manifests**: Use `kustomize` and `helm` skills for chart templating and overlays
- **GitOps**: Use `argocd` skill for ApplicationSets and sync configuration
- **Calico deep-dive**: A separate `calico` skill covers NetworkPolicy, BGP, Felix tuning (when available)
