# Talos Linux Architecture Reference (v1.12)

## Design Philosophy

- Immutable OS: runs from SquashFS image (<80MB), even when installed to disk
- No shell, no SSH, no package manager, no GNU utilities
- All management via gRPC API (talosctl)
- Single declarative YAML config for both Talos and Kubernetes
- Built from scratch in Go; minimal attack surface
- All disk writes replicated or reconstructable; ephemeral partition wiped on reset
- Kernel follows KSPP recommendations; dynamic modules disabled
- Certificates short-lived, auto-rotating

## Filesystem Layers

1. **Read-only base** - SquashFS loop-mounted in RAM
2. **Runtime tmpfs** - `/dev`, `/proc`, `/run`, `/sys`, `/tmp`, `/system`; bind mounts for `/etc/hosts`, `/etc/resolv.conf`
3. **Persistent overlayfs** - XFS-backed at `/var` (survives reboots, wiped on reset)

## Disk Partitions

| Partition | Purpose |
|-----------|---------|
| EFI/BIOS | Boot stage |
| BOOT | Kernel + initramfs |
| META | Node metadata/identifiers |
| STATE | Machine config, KubeSpan data |
| EPHEMERAL | Runtime state at `/var` (etcd, kubelet, containerd data) |

## Core Components

| Component | Role |
|-----------|------|
| **machined** | Init replacement. Manages config, API ops, resources/controllers. Runs: containerd, etcd, kubelet, networkd, trustd, udevd |
| **apid** | gRPC gateway; proxies requests to machined. Entry point for talosctl |
| **trustd** | PKI distribution via root-of-trust; enables cross-node trust during bootstrap |
| **containerd** | Container runtime. `system` namespace (Talos services), `k8s.io` namespace (Kubernetes) |
| **etcd** | Distributed KV store for Kubernetes |
| **kubelet** | Node agent; launches static pods for control plane |
| **udevd** | eudev fork; device management |

All components communicate via gRPC over local machine sockets.

## Control Plane Architecture

Control plane nodes (`.machine.type: controlplane`) run as static pods managed by kubelet:
- etcd, kube-apiserver, kube-controller-manager, kube-scheduler
- Tainted to prevent workload scheduling

### Bootstrap Sequence

1. etcd starts on all control plane nodes
2. kubelet starts cluster-wide
3. Bootstrap node initializes etcd as first member
4. Static pod definitions rendered to disk
5. kube-apiserver comes online
6. Bootstrap manifests apply join tokens + CSR auto-approval
7. All nodes register. Bootstrap node has no special role afterward

### etcd Quorum

- 3 nodes: tolerates 1 failure (recommended minimum)
- 5 nodes: tolerates 2 failures
- 2 nodes: unsafe (either failure loses quorum)
- Remove nodes with `talosctl reset` (must leave etcd cleanly)

## Controllers & Resources Model

**Resources** = discrete state pieces. Identified by tuple: (namespace, type, id).
- Metadata: namespace, type, ID (fixed)
- Spec: variable content per type
- Stored in memory (rebuilt on reboot) except MachineConfig

**Controllers** = independent threads running reconciliation loops.
- Multiple inputs, single output (one resource type per namespace)
- Exclusive ownership: one controller per resource type per namespace
- Triggers: resource changes, scheduled runs, external watches

**Namespaces**: `config`, `controlplane`, `meta`, `runtime`, `secrets`

Query resources: `talosctl get <type>`, `talosctl get <type> -o yaml`, `talosctl get <type> --watch`

## Talos vs Traditional Linux

| Traditional Linux | Talos Equivalent |
|-------------------|-----------------|
| SSH shell | `talosctl` API calls |
| systemd | Talos-native services |
| journalctl | `talosctl logs <service>` |
| Read/write filesystem | Read-only; `talosctl read` |
| Edit config files | `talosctl patch mc` / `talosctl apply-config` |
| top/htop | `talosctl dashboard` |
| ip/ethtool | `talosctl get addresses`, `talosctl get routes` |
| Package manager | System extensions |

See `references/architecture-discovery-talosctl.md` for cluster discovery, talosctl config, endpoints/nodes.
