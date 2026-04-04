---
last_updated: 2026-03-11
---

# IP Pool Management

## Default IPPool

```yaml
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: default-ipv4-ippool
spec:
  cidr: 10.42.0.0/16
  encapsulation: VXLAN
  natOutgoing: true
  nodeSelector: all()
  blockSize: 26              # /26 = 64 IPs per node block
  allowedUses:
    - Workload
    - Tunnel
```

## Key Fields

| Field | Default | Description |
|-------|---------|-------------|
| `cidr` | Required | Pool CIDR range |
| `encapsulation` | `VXLAN` | VXLAN, VXLANCrossSubnet, IPIP, IPIPCrossSubnet, None |
| `natOutgoing` | `false` | SNAT pod traffic leaving the cluster |
| `blockSize` | `26` (IPv4), `122` (IPv6) | Per-node allocation block size |
| `nodeSelector` | `all()` | Which nodes use this pool |
| `allowedUses` | `[Workload, Tunnel]` | Workload and/or Tunnel |
| `disableBGPExport` | `false` | Prevent BGP advertisement of this pool |
| `disabled` | `false` | Stop new allocations from this pool |

## Multiple Pools

Assign different pools to different node groups:

```yaml
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: zone-a-pool
spec:
  cidr: 10.42.0.0/17
  encapsulation: VXLAN
  natOutgoing: true
  nodeSelector: topology.kubernetes.io/zone == 'zone-a'
---
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: zone-b-pool
spec:
  cidr: 10.42.128.0/17
  encapsulation: VXLAN
  natOutgoing: true
  nodeSelector: topology.kubernetes.io/zone == 'zone-b'
```

## Namespace/Pod-Specific Pools

Use annotations to select a pool for specific workloads:

```yaml
# Namespace annotation
apiVersion: v1
kind: Namespace
metadata:
  name: special-apps
  annotations:
    cni.projectcalico.org/ipv4pools: '["special-pool"]'
```

```yaml
# Pod annotation
metadata:
  annotations:
    cni.projectcalico.org/ipv4pools: '["special-pool"]'
```

## Migrating Encapsulation Mode

To migrate from IPIP to VXLAN without downtime:

1. Create new VXLAN pool alongside existing IPIP pool
2. Disable old IPIP pool (`disabled: true`) -- stops new allocations
3. Rolling restart workloads to pick up new pool addresses
4. Delete old IPIP pool once all pods migrated

```bash
# Check which pool pods are using
calicoctl get wep --all-namespaces -o wide
# Verify no IPs from old pool remain
calicoctl ipam show --ip=10.42.x.x
```

## Dual-Stack (IPv4 + IPv6)

```yaml
apiVersion: projectcalico.org/v3
kind: IPPool
metadata:
  name: default-ipv6-ippool
spec:
  cidr: fd00:10:42::/48
  encapsulation: None          # IPv6 doesn't support VXLAN/IPIP
  natOutgoing: false
  blockSize: 122
```

Enable in Installation CR:

```yaml
spec:
  calicoNetwork:
    ipPools:
      - cidr: 10.42.0.0/16
        encapsulation: VXLAN
      - cidr: fd00:10:42::/48
        encapsulation: None
```

## Block Size Considerations

| blockSize | IPs/Node | Nodes Supported (for /16) | Use Case |
|-----------|----------|---------------------------|----------|
| 24 | 256 | 256 | Large nodes, many pods |
| 26 | 64 | 1024 | Default, balanced |
| 28 | 16 | 4096 | Many nodes, few pods each |
| 29 | 8 | 8192 | Maximum node count |

Changing blockSize on existing pool requires migration (create new pool, drain old).

## IPAM Commands

```bash
calicoctl ipam show                              # Overall utilization
calicoctl ipam show --show-blocks                # Per-node block allocation
calicoctl ipam show --ip=10.42.0.5               # Check specific IP
calicoctl ipam release --ip=10.42.0.5            # Release leaked IP
calicoctl ipam check                             # Consistency check
```
