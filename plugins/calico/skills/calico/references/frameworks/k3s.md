---
last_updated: 2026-03-11
---

# Calico on K3s / Rancher

## Enabling Calico on K3s

K3s ships with Flannel as default CNI. To use Calico instead:

### 1. Disable Flannel and built-in network policy

```bash
# Server node install
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server \
  --flannel-backend=none \
  --disable-network-policy \
  --cluster-cidr=10.42.0.0/16 \
  --service-cidr=10.43.0.0/16" sh -
```

**Flags explained:**

| Flag | Purpose |
|------|---------|
| `--flannel-backend=none` | Disables Flannel CNI entirely |
| `--disable-network-policy` | Disables K3s built-in network policy controller (Calico handles this) |
| `--cluster-cidr=10.42.0.0/16` | Pod CIDR — must match Calico IPPool |
| `--service-cidr=10.43.0.0/16` | Service CIDR — default K3s value |

Node stays `NotReady` until Calico is deployed and calico-node pod is running.

### 2. Install Calico via Tigera Operator

```bash
helm repo add projectcalico https://docs.tigera.io/calico/charts
helm install calico projectcalico/tigera-operator --version v3.29.3 \
  --namespace tigera-operator --create-namespace \
  -f values.yaml
```

**values.yaml** — ensure IPPool CIDR matches `--cluster-cidr`:

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

### 3. Firewall ports

```bash
# Control plane
TCP 6443   # K8s API server
TCP 10250  # Kubelet metrics

# Calico networking
UDP 4789   # VXLAN encapsulation
IP proto 4 # IPIP encapsulation (if using IPIP mode)
TCP 179    # BGP (if using BGP mode)
UDP 51820  # WireGuard (if encryption enabled)
```

## Disabling Calico on K3s

To revert to Flannel (or switch CNI):

### 1. Remove Calico

```bash
# Uninstall helm release
helm uninstall calico -n tigera-operator

# Remove CRDs (operator doesn't clean these up)
kubectl get crd | grep -E 'calico|tigera' | awk '{print $1}' | xargs kubectl delete crd

# Clean up namespaces
kubectl delete namespace calico-system calico-apiserver tigera-operator

# On each node — remove Calico network state
rm -rf /etc/cni/net.d/10-calico.conflist
rm -rf /etc/cni/net.d/calico-kubeconfig
rm -rf /var/lib/calico
rm -rf /var/run/calico
ip link delete vxlan.calico 2>/dev/null
ip link delete tunl0 2>/dev/null
```

### 2. Re-enable Flannel

Remove the `--flannel-backend=none` and `--disable-network-policy` flags from K3s config, then restart:

```bash
# Edit K3s config
# /etc/rancher/k3s/config.yaml — remove flannel-backend and disable-network-policy

systemctl restart k3s
```

## K3s Airgapped Deployment

For air-gapped environments, pre-load Calico images before K3s starts:

### Image directory

K3s auto-imports images from `/var/lib/rancher/k3s/agent/images/` on startup.

```bash
# Copy image tarballs
cp calico-images.tar.gz /var/lib/rancher/k3s/agent/images/

# K3s imports on start — no manual load needed
systemctl restart k3s
```

### Required images

```
quay.io/tigera/operator:<version>
quay.io/calico/node:<version>
quay.io/calico/typha:<version>
quay.io/calico/kube-controllers:<version>
quay.io/calico/cni:<version>
quay.io/calico/apiserver:<version>
quay.io/calico/pod2daemon-flexvol:<version>
docker.io/calico/ctl:<version>
```

### imagePullPolicy

With airgap, all Calico pods must use `imagePullPolicy: Never` or `IfNotPresent`. Apply via kustomize overlay on the rendered Helm output, or patch the Installation CR:

```yaml
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  # imagePullSecrets: [] # No secrets needed for pre-loaded images
  registry: ""           # Empty = use default image names
```

## K3s HA with Calico

For multi-server K3s with embedded etcd:

```bash
# First server
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server \
  --cluster-init \
  --flannel-backend=none \
  --disable-network-policy \
  --tls-san=<load-balancer-ip>" sh -

# Additional servers
curl -sfL https://get.k3s.io | K3S_TOKEN=<token> INSTALL_K3S_EXEC="server \
  --server https://<first-server>:6443 \
  --flannel-backend=none \
  --disable-network-policy" sh -
```

Install Calico only once after first server is up. Calico DaemonSet auto-deploys to all nodes.

## Rancher-Managed Clusters

When using Rancher to provision RKE2/K3s clusters:

### Via Rancher UI

1. Cluster Management > Create > Custom
2. Under **Cluster Configuration > Networking**:
   - Set **Container Network Interface** to `Calico`
   - Rancher handles Flannel disable + Calico install automatically

### Via Rancher API / Fleet

```yaml
apiVersion: provisioning.cattle.io/v1
kind: Cluster
metadata:
  name: my-cluster
spec:
  rkeConfig:
    machineGlobalConfig:
      cni: calico
      # Automatically sets flannel-backend=none + installs Calico
```

### RKE2 (Rancher's Kubernetes)

RKE2 ships with Calico as the default CNI (not Flannel). No special flags needed:

```bash
# RKE2 uses Calico by default
curl -sfL https://get.rke2.io | sh -
systemctl enable --now rke2-server
```

Override via `/etc/rancher/rke2/config.yaml`:

```yaml
cni:
  - calico    # default
  # - canal   # alternative (Calico policy + Flannel networking)
  # - cilium  # alternative
```

## Troubleshooting K3s + Calico

| Symptom | Cause | Fix |
|---------|-------|-----|
| Node stuck NotReady after install | Calico not deployed yet, or image pull failure | Check `kubectl get pods -n calico-system`, verify images loaded |
| `10-flannel.conflist` conflicts | Flannel not fully disabled | Remove `/etc/cni/net.d/10-flannel.conflist`, restart K3s |
| Pods get Flannel IPs | Old Flannel CNI config still present | Remove `/etc/cni/net.d/10-flannel*`, restart kubelet |
| `cni0` bridge still exists | Stale Flannel bridge device | `ip link delete cni0`, restart K3s |
| VXLAN not working | UDP 4789 blocked between nodes | Check firewall rules on all nodes |
| Pod CIDR mismatch | `--cluster-cidr` != IPPool CIDR | Align K3s flag with Calico IPPool `cidr` |
