# Talos Architecture: Discovery & talosctl Reference (v1.12)

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
