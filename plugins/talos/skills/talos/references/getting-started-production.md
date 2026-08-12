# Talos Linux v1.12 Production Cluster Setup

## Production Cluster (3 Control Planes)

### Key differences from single-node setup

- 3 control plane nodes minimum for HA
- Load balancer or DNS round-robin for API endpoints
- Separate secrets bundle generation
- Config patching for per-node customization

### Kubernetes endpoint options

**Option A -- Dedicated LB:** TCP LB on port 6443 -> all CP nodes.
**Option B -- DNS round-robin:**
```
kube.cluster1.example.com  IN  A  192.168.0.10
kube.cluster1.example.com  IN  A  192.168.0.11
kube.cluster1.example.com  IN  A  192.168.0.12
```

### Talos API load balancer

TCP LB on port 50000 -> all CP nodes. Must be TCP, not HTTP (gRPC + mTLS).

### Production bootstrap steps

```bash
CONTROL_PLANE_IP=("192.168.0.2" "192.168.0.3" "192.168.0.4")
WORKER_IP=("192.168.0.5" "192.168.0.6")

# Generate secrets separately (store securely)
talosctl gen secrets -o secrets.yaml

# Generate configs with secrets + endpoint
export CLUSTER_NAME=prod-cluster
export YOUR_ENDPOINT=kube.cluster1.example.com
talosctl gen config --with-secrets secrets.yaml $CLUSTER_NAME https://$YOUR_ENDPOINT:6443

# Check hardware
talosctl --nodes <ip> get links --insecure    # network interfaces
talosctl get disks --insecure --nodes <ip>     # disks

# Patch configs per-node (network interface, install disk)
cat <<'PATCH' > controlplane-patch.yaml
machine:
  network:
    interfaces:
      - interface: eth0
        dhcp: true
  install:
    disk: /dev/sda
PATCH
talosctl machineconfig patch controlplane.yaml --patch @controlplane-patch.yaml --output controlplane.yaml
talosctl machineconfig patch worker.yaml --patch @worker-patch.yaml --output worker.yaml

# Apply to all nodes
for ip in "${CONTROL_PLANE_IP[@]}"; do
  talosctl apply-config --insecure --nodes $ip --file controlplane.yaml
done
for ip in "${WORKER_IP[@]}"; do
  talosctl apply-config --insecure --nodes $ip --file worker.yaml
done

# Merge talosconfig into default location
talosctl config merge ./talosconfig
# Or: cp ./talosconfig ~/.talos/config && export TALOSCONFIG=~/.talos/config

# Set all CP endpoints (enables client-side LB + failover)
talosctl config endpoint 192.168.0.2 192.168.0.3 192.168.0.4

# Bootstrap (ONCE, one CP node)
talosctl bootstrap --nodes 192.168.0.2

# Get kubeconfig
talosctl kubeconfig --nodes 192.168.0.2

kubectl get nodes
```

### Production notes

- Unmount install media before applying config
- Multihomed machines (multiple IPs) need extra config per Multihoming docs
- Configured endpoint = fallback if KubePrism unavailable (e.g. after reboot)
- Omni platform automates large-scale management + acts as LB
