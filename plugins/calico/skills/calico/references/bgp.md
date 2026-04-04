---
last_updated: 2026-03-11
---

# BGP Configuration

## Overview

Calico supports BGP for native routing (no VXLAN/IPIP overlay). Modes:

| Mode | Description |
|------|-------------|
| Full mesh | All nodes peer with each other (default when BGP enabled) |
| Route reflectors | Designated nodes redistribute routes (scales beyond ~100 nodes) |
| External peering | Peer with ToR switches or routers |

## BGPConfiguration

Global BGP settings (must be named `default`):

```yaml
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  asNumber: 64512               # Cluster AS number
  nodeToNodeMeshEnabled: true   # Full mesh (disable for route reflectors)
  listenPort: 179               # BGP listen port
  logSeverityScreen: Info
  serviceClusterIPs:            # Advertise ClusterIP ranges
    - cidr: 10.43.0.0/16
  serviceExternalIPs:           # Advertise external IPs
    - cidr: 203.0.113.0/24
  serviceLoadBalancerIPs:       # Advertise LB IPs
    - cidr: 198.51.100.0/24
```

## External BGP Peer

Peer with a ToR switch or router:

```yaml
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: tor-switch
spec:
  peerIP: 192.168.1.1
  asNumber: 64513               # Remote AS
  keepOriginalNextHop: false
  nodeSelector: rack == 'rack1' # Which nodes peer with this
```

### Per-Node Peering

```yaml
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: node1-peer
spec:
  peerIP: 192.168.1.1
  asNumber: 64513
  node: node1                   # Specific node (alternative to nodeSelector)
```

## Route Reflectors

For clusters with >100 nodes, use route reflectors instead of full mesh:

### 1. Disable full mesh

```yaml
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  nodeToNodeMeshEnabled: false
  asNumber: 64512
```

### 2. Label route reflector nodes

```bash
kubectl label node rr-node-1 route-reflector=true
kubectl annotate node rr-node-1 projectcalico.org/RouteReflectorClusterID=1.0.0.1
```

### 3. Configure RR peering

```yaml
# Non-RR nodes peer with RR nodes
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: peer-to-rr
spec:
  peerSelector: route-reflector == 'true'
  nodeSelector: '!has(route-reflector)'
---
# RR nodes peer with each other
apiVersion: projectcalico.org/v3
kind: BGPPeer
metadata:
  name: rr-mesh
spec:
  peerSelector: route-reflector == 'true'
  nodeSelector: route-reflector == 'true'
```

## BGP Communities

Tag routes with communities for upstream filtering:

```yaml
apiVersion: projectcalico.org/v3
kind: BGPConfiguration
metadata:
  name: default
spec:
  prefixAdvertisements:
    - cidr: 10.42.0.0/16
      communities:
        - name: internal-pods
          value: '64512:100'
    - cidr: 10.43.0.0/16
      communities:
        - name: cluster-services
          value: '64512:200'
```

## BGP Filters

Control which routes are imported/exported per peer:

```yaml
apiVersion: projectcalico.org/v3
kind: BGPFilter
metadata:
  name: allow-pod-cidr-only
spec:
  exportV4:
    - action: Accept
      matchOperator: In
      cidr: 10.42.0.0/16
    - action: Reject
  importV4:
    - action: Accept
      matchOperator: In
      cidr: 10.0.0.0/8
    - action: Reject
```

Attach to a BGPPeer:

```yaml
spec:
  filters:
    - allow-pod-cidr-only
```

## Verification

```bash
# Node BGP status
calicoctl node status

# Check specific peer
calicoctl get bgppeer -o wide

# View advertised routes (from calico-node pod)
kubectl exec -n calico-system <calico-node-pod> -- birdcl show route

# BGP session state
kubectl exec -n calico-system <calico-node-pod> -- birdcl show protocols
```

## Common Issues

| Symptom | Cause |
|---------|-------|
| BGP session stuck in Connect | Firewall blocking TCP 179 |
| Routes not propagated | Wrong AS number or nodeSelector |
| Asymmetric routing | Missing `keepOriginalNextHop` setting |
| RR not reflecting | Missing RouteReflectorClusterID annotation |
