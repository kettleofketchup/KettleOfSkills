---
name: talos
description: Talos Linux v1.12 Kubernetes operating system management. This skill should be used when bootstrapping Talos clusters, generating or patching machine configurations (controlplane.yaml, worker.yaml), configuring networking (static IPs, VLANs, bonds, bridges, DNS, proxies, KubeSpan, firewall rules), upgrading Talos OS or Kubernetes versions, performing etcd maintenance (backup, restore, defrag, member management), troubleshooting cluster issues (talosctl commands, logs, health checks, dashboard), managing storage (disk encryption, user volumes, Rook-Ceph, local-path-provisioner), deploying Kubernetes addons (Cilium, Calico, MetalLB, Traefik, metrics-server), installing on platforms (bare metal ISO/PXE, Proxmox, KVM, VMware, Docker, air-gapped), managing security (certificates, CA rotation, SecureBoot, SELinux), or working with system extensions, containerd config, registry mirrors, and performance tuning.
---

# Talos Linux

Talos is an immutable, API-driven Linux distribution purpose-built for Kubernetes. No SSH, no shell,
no package manager. All management via `talosctl` API. Machine config is a single YAML file
containing one or more documents separated by `---`.

## Quick Reference

| Task | Command |
|------|---------|
| Install talosctl | `brew install siderolabs/tap/talosctl` |
| Generate secrets | `talosctl gen secrets -o secrets.yaml` |
| Generate config | `talosctl gen config <name> <endpoint> --with-secrets secrets.yaml` |
| Apply config | `talosctl apply-config -n <ip> -f config.yaml --insecure` |
| Bootstrap cluster | `talosctl bootstrap -n <cp-ip> -e <cp-ip>` |
| Get kubeconfig | `talosctl kubeconfig -n <cp-ip>` |
| Upgrade Talos | `talosctl upgrade -n <ip> --image ghcr.io/siderolabs/installer:v1.12.x` |
| Upgrade K8s | `talosctl upgrade-k8s -n <cp-ip> --to 1.x.y` |
| Check health | `talosctl health` |
| View dashboard | `talosctl dashboard` |
| Patch config | `talosctl patch mc -n <ip> --patch @patch.yaml` |
| etcd snapshot | `talosctl etcd snapshot db.snapshot` |
| Reset node | `talosctl reset -n <ip>` |
| View logs | `talosctl logs <service> -n <ip>` |
| Kernel logs | `talosctl dmesg -n <ip>` |

## Machine Config Structure

Config = multi-document YAML. Primary document is `v1alpha1` with `machine:` and `cluster:` sections.
Additional documents for networking (LinkConfig, VLANConfig, BondConfig, etc.), storage (VolumeConfig,
UserVolumeConfig), firewall (NetworkRuleConfig), and extensions (ExtensionServiceConfig).

Key config operations:
- **Generate**: `talosctl gen config` with `--config-patch` flags
- **Patch**: strategic merge patches (`machine:` partial YAML merged with base)
- **Apply modes**: `auto`, `no-reboot`, `reboot`, `staged`, `try`
- **Edit live**: `talosctl edit mc -n <ip>`

See `references/machine-config.md` for full v1alpha1 schema, patching rules, and examples.

## Cluster Lifecycle

### Bootstrap
1. Generate secrets (`gen secrets`) - store permanently
2. Generate configs with patches (`gen config` + `--config-patch`)
3. Boot nodes with Talos ISO/PXE
4. Apply configs (`apply-config --insecure`)
5. Bootstrap ONE control plane (`talosctl bootstrap`)
6. Retrieve kubeconfig

See `references/getting-started.md` for complete bootstrap procedures (single-node and production HA).

### Upgrades
- **Talos OS**: `talosctl upgrade --image <installer>` - A/B image, auto-rollback on boot failure
- **Kubernetes**: `talosctl upgrade-k8s --to <version>` - handles all components automatically
- **etcd**: backup with `etcd snapshot`, restore with `bootstrap --recover-from`

See `references/upgrades-maintenance.md` for full procedures, rollback, and disaster recovery.

## Networking

Talos uses config documents for network setup. No network config = DHCP on primary interface.

Key topics: static IPs, VLANs, bonds, bridges, DNS resolvers, corporate proxies, KubeSpan
(WireGuard mesh), ingress firewall, multihoming (etcd/kubelet subnet selection).

See `references/networking.md` for all network config document types and YAML examples.

## Storage

Talos disk: EFI + META + STATE + EPHEMERAL partitions. Supports LUKS2 encryption (nodeID, TPM, KMS keys).
User volumes for workload storage. CSI drivers: Rook-Ceph, Longhorn, local-path-provisioner.

See `references/storage.md` for disk management, encryption, user volumes, and Rook-Ceph setup.

## Kubernetes Addons

Common addons on Talos: Cilium/Calico (CNI), MetalLB (LoadBalancer), Traefik (Gateway API),
metrics-server, KubePrism (in-cluster HA endpoint). Deploy via Helm, extraManifests, or inlineManifests.

See `references/kubernetes-addons.md` for deployment procedures and config patches.

## Troubleshooting

Diagnostic workflow: `talosctl health` → `talosctl services` → `talosctl logs <svc>` →
`talosctl dmesg` → `talosctl get <resource>` → `talosctl dashboard`.

See `references/troubleshooting.md` for common issues, diagnostic commands, and recovery procedures.

## References

| File | Topics |
|------|--------|
| `references/getting-started.md` | Bootstrap, quickstart, production notes, system requirements |
| `references/machine-config.md` | v1alpha1 schema, patching, apply modes, config generation |
| `references/networking.md` | Static IP, VLAN, bond, bridge, DNS, proxy, KubeSpan, firewall |
| `references/upgrades-maintenance.md` | Talos/K8s upgrades, etcd ops, disaster recovery, scaling |
| `references/troubleshooting.md` | Diagnostics, common issues, talosctl commands, logging |
| `references/storage.md` | Disk management, encryption, user volumes, Rook-Ceph, CSI |
| `references/kubernetes-addons.md` | Cilium, Calico, MetalLB, Traefik, metrics-server, KubePrism |
| `references/installation-platforms.md` | Bare metal, Proxmox, KVM, VMware, Docker, air-gapped |
| `references/security.md` | Certificates, CA rotation, SecureBoot, SELinux, image verification |
| `references/architecture.md` | Components, control plane, controllers/resources, philosophy |
| `references/extensions-customization.md` | Extensions, kernel modules, containerd, registry mirrors, tuning |

Official docs: https://docs.siderolabs.com/talos/v1.12/
