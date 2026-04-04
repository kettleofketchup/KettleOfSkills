---
name: calico
description: Calico CNI and network policy engine via Tigera Operator for Kubernetes. Use when deploying Calico with Tigera Operator Helm chart, configuring IPPools (VXLAN/IPIP/BGP encapsulation), writing Calico NetworkPolicy or GlobalNetworkPolicy resources, setting up BGP peering (BGPPeer, BGPConfiguration, route reflectors), tuning FelixConfiguration (BPF dataplane, iptables, logging, flow logs), upgrading Calico versions, enabling or disabling Calico on K3s/RKE2/Rancher clusters, configuring airgapped Calico deployments, or troubleshooting pod networking issues (node NotReady, DNS failures, cross-node connectivity, VXLAN/IPIP tunnel problems).
last_updated: 2026-03-11
---

# Calico

Kubernetes CNI and network policy engine deployed via Tigera Operator. Provides pod networking (VXLAN, IPIP, or native BGP), network policy enforcement, and optional BPF dataplane.

## Architecture

```
Tigera Operator (manages lifecycle)
├── calico-node (DaemonSet) - BGP, routing, Felix agent
├── calico-typha (Deployment) - fan-out datastore cache
├── calico-kube-controllers - sync K8s resources to Calico
├── calico-apiserver - Calico API extension
└── CRDs - IPPool, NetworkPolicy, BGP*, Felix*, etc.
```

## Deployment via Tigera Operator

### Helm Install

```bash
helm repo add projectcalico https://docs.tigera.io/calico/charts
helm install calico projectcalico/tigera-operator --version v3.29.3 \
  --namespace tigera-operator --create-namespace -f values.yaml
```

### Minimal values.yaml

```yaml
tigera-operator:
  installation:
    calicoNetwork:
      ipPools:
        - cidr: 10.42.0.0/16
          encapsulation: VXLAN
          natOutgoing: true
          nodeSelector: all()
```

For K3s/Rancher integration (enable/disable, airgap, HA), see `references/frameworks/k3s.md`.

### Upgrade

```bash
# 1. Check compatibility matrix: https://docs.tigera.io/calico/latest/getting-started/kubernetes/requirements
# 2. Update chart
helm repo update
helm upgrade calico projectcalico/tigera-operator --version v3.29.3 \
  --namespace tigera-operator -f values.yaml
# 3. Monitor rollout
kubectl rollout status daemonset/calico-node -n calico-system
kubectl get tigerastatus
```

## IP Pools & Encapsulation

| Mode | Field | Use Case |
|------|-------|----------|
| VXLAN | `encapsulation: VXLAN` | Default, works across L3 networks |
| VXLANCrossSubnet | `encapsulation: VXLANCrossSubnet` | VXLAN only for cross-subnet |
| IPIP | `encapsulation: IPIP` | Legacy, tunnel-based |
| IPIPCrossSubnet | `encapsulation: IPIPCrossSubnet` | IPIP only for cross-subnet |
| None | `encapsulation: None` | Native routing / BGP peering required |

For IP pool management (multiple pools, node-specific pools, migration), see `references/ip-pools.md`.

## Network Policy

Calico extends Kubernetes NetworkPolicy with richer selectors and global scope:

| Resource | Scope | Key Features |
|----------|-------|--------------|
| `NetworkPolicy` | Namespaced | L3-L7 rules, DNS policy, service accounts |
| `GlobalNetworkPolicy` | Cluster-wide | Host endpoint protection, ordered evaluation |

```yaml
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: allow-web
  namespace: default
spec:
  selector: app == 'web'
  ingress:
    - action: Allow
      source:
        selector: app == 'frontend'
      destination:
        ports: [80, 443]
  egress:
    - action: Allow
```

For policy patterns (deny-all, DNS allow, egress control, host endpoints), see `references/network-policy.md`.

## BGP Configuration

For environments using native routing instead of overlay:

```yaml
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  asNumber: 64512
  nodeToNodeMeshEnabled: true
  listenPort: 179
```

For BGP peering (external peers, route reflectors, communities, BGPFilter), see `references/bgp.md`.

## Felix Configuration

Felix is the per-node agent handling policy enforcement and routing:

```yaml
apiVersion: projectcalico.org/v3
kind: FelixConfiguration
metadata:
  name: default
spec:
  bpfEnabled: false          # true for BPF dataplane
  logSeverityScreen: Info     # Debug, Info, Warning, Error, Fatal
  ipipEnabled: true
  vxlanEnabled: true
```

For advanced Felix tuning (BPF dataplane, flow logs, connection tracking, MTU, wireguard), see `references/felix.md`.

## Troubleshooting

**First commands:**

```bash
kubectl get tigerastatus                    # overall health
kubectl get pods -n calico-system           # component status
kubectl get ippool -o yaml                  # pool config
calicoctl node status                       # BGP peering state
```

For debugging workflows (node NotReady, cross-node failures, DNS issues, VXLAN/IPIP problems), see `references/troubleshooting.md`.

## Common Issues

| Symptom | Likely Cause | Reference |
|---------|--------------|-----------|
| Node stuck NotReady | Calico-node crashloop, IPPool misconfigured | troubleshooting.md |
| Pods can't reach other nodes | VXLAN/IPIP port blocked (UDP 4789/IP proto 4) | troubleshooting.md |
| DNS resolution fails | NetworkPolicy blocking CoreDNS egress | network-policy.md |
| BGP session down | Wrong AS number, firewall blocking TCP 179 | bgp.md |
| High CPU on calico-node | Felix log level Debug, excessive policies | felix.md |
| "Failed to discover tenancy mode" | CRDs not applied before operator start (v3.28.3+) | troubleshooting.md |

## Upstream Docs

- Installation: https://docs.tigera.io/calico/latest/getting-started/
- CRD reference: https://docs.tigera.io/calico/latest/reference/resources/
- Felix config: https://docs.tigera.io/calico/latest/reference/resources/felixconfig
- calicoctl: https://docs.tigera.io/calico/latest/operations/calicoctl/

## References

- `references/ip-pools.md` - IP pool management, multiple pools, migration
- `references/network-policy.md` - Policy patterns, deny-all, DNS, host endpoints
- `references/bgp.md` - BGP peering, route reflectors, communities, filters
- `references/felix.md` - Felix tuning, BPF dataplane, flow logs, wireguard
- `references/troubleshooting.md` - Debugging pod networking, node issues
- `references/frameworks/k3s.md` - K3s/Rancher: enable, disable, airgap, HA
