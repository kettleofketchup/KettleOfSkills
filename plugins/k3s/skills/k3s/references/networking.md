# K3s Networking

## Flannel Backends

K3s bundles Flannel as default CNI. Backend set via `--flannel-backend`:

| Backend | Description | Requirements |
|---------|-------------|--------------|
| `vxlan` | Default. UDP encapsulation | Kernel VXLAN module |
| `host-gw` | Direct IP routes via node IPs | Layer 2 adjacency between nodes |
| `wireguard-native` | Encrypted WireGuard tunnels | WireGuard kernel module |
| `none` | **Disable Flannel entirely** | Must deploy external CNI |

**Flannel flags must be identical on ALL server nodes.**

## Replacing Flannel with Custom CNI

### Required Flags

```yaml
# /etc/rancher/k3s/config.yaml
flannel-backend: "none"
disable-network-policy: true
```

Or CLI: `--flannel-backend=none --disable-network-policy`

Both flags are required — `disable-network-policy` prevents K3s from deploying its built-in kube-router-based network policy controller.

### Calico with Tigera Operator

1. **K3s config** — disable flannel + network policy (above)

2. **Install tigera-operator** via Helm:

```bash
helm repo add projectcalico https://docs.tigera.io/calico/charts
helm install calico projectcalico/tigera-operator \
  --namespace tigera-operator --create-namespace \
  --set installation.calicoNetwork.ipPools[0].cidr=10.42.0.0/16 \
  --set installation.calicoNetwork.ipPools[0].encapsulation=VXLAN \
  --set installation.calicoNetwork.ipPools[0].natOutgoing=true \
  --set installation.calicoNetwork.ipPools[0].nodeSelector="all()"
```

3. **Values file** for vendored chart:

```yaml
# values.yaml
tigera-operator:
  installation:
    calicoNetwork:
      ipPools:
        - cidr: 10.42.0.0/16        # Must match K3s --cluster-cidr
          encapsulation: VXLAN
          natOutgoing: true
          nodeSelector: all()
```

4. **IP forwarding** — Calico CNI plugin config needs:

```json
"container_settings": {
  "allow_ip_forwarding": true
}
```

Verify: `cat /etc/cni/net.d/10-calico.conflist`

### Cilium

```bash
helm repo add cilium https://helm.cilium.io/
helm install cilium cilium/cilium --namespace kube-system
```

**Cleanup before uninstall** (Cilium leaves artifacts):
```bash
ip link delete cilium_host; ip link delete cilium_net; ip link delete cilium_vxlan
iptables-save | grep -iv cilium | iptables-restore
```

## Firewall Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 6443 | TCP | K3s API server |
| 10250 | TCP | Kubelet metrics |
| 8472 | UDP | VXLAN (Flannel/Calico) |
| 51820 | UDP | WireGuard (if enabled) |
| 51821 | UDP | WireGuard IPv6 |
| 2379-2380 | TCP | etcd (HA mode) |
| 179 | TCP | BGP (Calico with BGP peering) |

## Dual-Stack Networking

Configure at cluster creation (cannot enable later):

```yaml
cluster-cidr: "10.42.0.0/16,2001:db8:42::/56"
service-cidr: "10.43.0.0/16,2001:db8:43::/112"
```

For non-public IPv6 (ULA), add: `--flannel-ipv6-masq`

## Control-Plane Egress Modes

`--egress-selector-mode` (server flag):

| Mode | Description |
|------|-------------|
| `disabled` | Direct node connectivity required |
| `agent` | Default. API server routes through agent tunnel |
| `pod` | Routes via Nodes/Endpoints watching |
| `cluster` | Highest portability, more overhead |

## DNS Configuration

- `--cluster-dns` (default: `10.43.0.10`) — CoreDNS ClusterIP
- `--resolv-conf` — passed to kubelet, useful in airgap for custom DNS
- CoreDNS can be disabled (`--disable=coredns`) and replaced
