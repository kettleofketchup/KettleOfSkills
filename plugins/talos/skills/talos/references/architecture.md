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

## Network Connectivity

### Talos-Specific Ports

| Port | Protocol | Service | Direction | Used By |
|------|----------|---------|-----------|---------|
| 50000 | TCP | apid | Inbound (CP+worker) | talosctl, other CP nodes |
| 50001 | TCP | trustd | Inbound (CP only) | Worker nodes |

Ports not currently configurable. Additional Kubernetes ports required (see upstream docs).
Simplest deployment: full layer 2 connectivity between all nodes.

## Cluster Discovery

Aggregates peers from discovery registries. Two backends:

### Service Registry (default)
- External service at `https://discovery.talos.dev/` (TCP 443)
- Independent of etcd/Kubernetes availability
- AES-GCM encrypted; server stores opaque blobs
- Cluster isolation via cluster ID
- Can self-host (commercial license)

### Kubernetes Registry (deprecated)
- Uses K8s Node annotations; incompatible with K8s 1.32+ defaults

### Resource Types
- **Identities** - unique node ID (base62, persists across reboots)
- **Affiliates** - proposed members sharing cluster ID + secret
- **Members** - verified affiliates

Disable service registry:
```yaml
cluster:
  discovery:
    enabled: true
    registries:
      service:
        disabled: true
```

Disabling discovery impacts: KubeSpan (requires it), bootstrap/recovery speed, endpoint resolution.

## talosctl Deep Dive

Config location: `$HOME/.talos/config` (override: `TALOSCONFIG` env or `--talosconfig` flag).
Context system like kubectl; multiple clusters in one config file.

### Endpoints vs Nodes

**Endpoints** (`-e`): what talosctl connects to directly.
- Set to CP nodes, load balancer, or DNS name
- Multiple endpoints = automatic load balancing + failover
- Proxy requests to target nodes via mTLS

**Nodes** (`-n`): target machines for API calls.
- IPs/hostnames as seen from endpoints, not from client
- All connections proxied through endpoints (certificate-based auth)
- Recommend explicit `-n` flag over config file setting

### Kubeconfig
`talosctl kubeconfig` merges into default kubeconfig (safe, non-destructive).
`talosctl kubeconfig /path/to/file` writes to alternate location.
`--force` overwrites existing context with same name.
