---
last_updated: 2026-03-11
---

# Network Policy

## Calico vs Kubernetes NetworkPolicy

| Feature | K8s NetworkPolicy | Calico NetworkPolicy | Calico GlobalNetworkPolicy |
|---------|-------------------|---------------------|---------------------------|
| Scope | Namespaced | Namespaced | Cluster-wide |
| L3/L4 rules | Yes | Yes | Yes |
| Deny rules | Implicit only | Explicit `Deny` action | Explicit `Deny` action |
| Ordered evaluation | No | Yes (`order` field) | Yes (`order` field) |
| DNS policy | No | Yes | Yes |
| Service account selector | No | Yes | Yes |
| Host endpoint support | No | No | Yes |
| HTTP match (L7) | No | Yes | Yes |
| `Log` action | No | Yes | Yes |

## Default Deny (Best Practice)

Apply per-namespace to enforce explicit allow rules:

```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: default-deny
spec:
  order: 1000
  selector: all()
  types:
    - Ingress
    - Egress
```

Or per-namespace with Kubernetes NetworkPolicy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## Allow DNS (Required with Default Deny)

```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-dns
spec:
  order: 100
  selector: all()
  egress:
    - action: Allow
      destination:
        selector: k8s-app == 'kube-dns'
        ports: [53]
      protocol: UDP
    - action: Allow
      destination:
        selector: k8s-app == 'kube-dns'
        ports: [53]
      protocol: TCP
```

## Selector Syntax

Calico uses its own label selector syntax (not K8s label selectors):

```
# Equality
app == 'web'
app != 'db'

# Set membership
app in {'web', 'api'}
app not in {'db', 'cache'}

# Existence
has(app)
!has(internal)

# Logical operators
app == 'web' && env == 'prod'
app == 'web' || app == 'api'

# Global selector (all endpoints)
all()
```

## Egress Control

### Allow specific external CIDRs

```yaml
apiVersion: projectcalico.org/v3
kind: NetworkPolicy
metadata:
  name: allow-external-api
  namespace: myapp
spec:
  selector: app == 'myapp'
  egress:
    - action: Allow
      destination:
        nets: ['203.0.113.0/24']
        ports: [443]
      protocol: TCP
```

### Block metadata endpoint

```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: deny-cloud-metadata
spec:
  order: 50
  selector: all()
  egress:
    - action: Deny
      destination:
        nets: ['169.254.169.254/32']
```

## Policy Ordering

Lower `order` value = evaluated first. Policies without `order` evaluated last.

```
order: 10   ← evaluated first (highest priority)
order: 100  ← evaluated second
order: 1000 ← evaluated third
(no order)  ← evaluated last
```

First matching rule wins. If no rule matches, traffic is allowed (unless default deny exists).

## Host Endpoint Protection

Protect node-level traffic (SSH, kubelet):

```yaml
apiVersion: projectcalico.org/v3
kind: HostEndpoint
metadata:
  name: node1-eth0
  labels:
    node: node1
spec:
  interfaceName: eth0
  node: node1
---
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-ssh
spec:
  order: 100
  selector: has(node)
  ingress:
    - action: Allow
      source:
        nets: ['10.0.0.0/8']
      destination:
        ports: [22]
      protocol: TCP
  applyOnForward: false
```

## L7 (HTTP) Match

Requires Envoy sidecar or service mesh:

```yaml
spec:
  ingress:
    - action: Allow
      http:
        methods: ['GET', 'HEAD']
        paths:
          - exact: /healthz
          - prefix: /api/v1/
```

## Logging Policy Hits

```yaml
spec:
  ingress:
    - action: Log       # Log then continue evaluation
    - action: Allow
      source:
        selector: app == 'frontend'
```

View logs: `kubectl logs -n calico-system -l k8s-app=calico-node | grep calico-packet`.

## Troubleshooting Policies

```bash
# List all policies in order
calicoctl get networkpolicy -A -o wide
calicoctl get globalnetworkpolicy -o wide

# Check which policies apply to a pod
calicoctl get wep -n <namespace> --output yaml | grep -A5 policy

# Verify Felix is enforcing
kubectl exec -n calico-system <calico-node-pod> -- calico-node -felix-live
```
