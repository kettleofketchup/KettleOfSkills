# Talos Linux v1.12 Getting Started Reference

## System Requirements

| Role | CPU | RAM | Disk (min) | Disk (rec) |
|------|-----|-----|------------|------------|
| Control Plane | 2 cores | 2 GiB | 10 GiB | 100 GiB |
| Worker | 1 core | 1 GiB | 10 GiB | 100 GiB |

Talos OS itself < 100 MB. Ephemeral partition (container images, work dirs) needs the rest.
Auto-creates EFI, META, STATE, EPHEMERAL partitions; EPHEMERAL expands to fill disk.
Production: use separate disks for OS and workload storage.

## Install talosctl

```bash
# Homebrew (recommended, auto-updates)
brew install siderolabs/tap/talosctl

# Installer script (macOS, Linux, WSL; amd64/arm64)
curl -sL https://talos.dev/install | sh

# Manual: download from GitHub releases, place in $PATH
```

talosctl version MUST match Talos Linux version on hosts.

## Quickstart (Docker)

```bash
talosctl cluster create docker
talosctl dashboard --nodes 10.5.0.2
kubectl get nodes -o wide
talosctl cluster destroy   # cleanup
```

macOS Docker Desktop fix if socket error:
```bash
sudo ln -s "$HOME/.docker/run/docker.sock" /var/run/docker.sock
```

## Cluster Bootstrap (Single Control Plane)

```bash
# Store IPs
export CONTROL_PLANE_IP=<cp-ip>
WORKER_IP=("<w1>" "<w2>")

# Check disks (before config)
talosctl get disks --insecure --nodes $CONTROL_PLANE_IP

# Generate config
export CLUSTER_NAME=mycluster
talosctl gen config $CLUSTER_NAME https://$CONTROL_PLANE_IP:6443 --install-disk /dev/sda
# outputs: controlplane.yaml, worker.yaml, talosconfig

# Apply configs
talosctl apply-config --insecure --nodes $CONTROL_PLANE_IP --file controlplane.yaml
for ip in "${WORKER_IP[@]}"; do
  talosctl apply-config --insecure --nodes "$ip" --file worker.yaml
done

# Set endpoint
talosctl --talosconfig=./talosconfig config endpoints $CONTROL_PLANE_IP

# Bootstrap etcd (ONCE, single CP node only)
talosctl bootstrap --nodes $CONTROL_PLANE_IP --talosconfig=./talosconfig

# Get kubeconfig
talosctl kubeconfig --nodes $CONTROL_PLANE_IP --talosconfig=./talosconfig

# Verify
talosctl --nodes $CONTROL_PLANE_IP --talosconfig=./talosconfig health
kubectl get nodes
```

ISO runs in RAM -- no disk changes until config applied.

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

## Deploy First Workload

```bash
kubectl apply -f https://raw.githubusercontent.com/siderolabs/example-workload/refs/heads/main/deploy/example-svc-nodeport.yaml
kubectl get pods,services

NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'; echo)
NODE_PORT=$(kubectl get svc example-workload -o jsonpath='{.spec.ports[0].nodePort}')
curl http://$NODE_IP:$NODE_PORT
```

Next steps: Pod Security, CSI persistent storage, Metrics Server.

## Key talosctl Commands

| Command | Purpose |
|---------|---------|
| `talosctl gen secrets -o secrets.yaml` | Generate secrets bundle |
| `talosctl gen config NAME URL` | Generate controlplane.yaml, worker.yaml, talosconfig |
| `talosctl apply-config --insecure -n IP -f FILE` | Apply config to unconfigured node |
| `talosctl machineconfig patch FILE --patch @PATCH` | Patch machine config with YAML |
| `talosctl config merge ./talosconfig` | Merge talosconfig into default |
| `talosctl config endpoint IP1 IP2 ...` | Set API endpoints (client-side LB) |
| `talosctl bootstrap -n IP` | Init etcd (once, single CP) |
| `talosctl kubeconfig -n IP` | Retrieve kubeconfig |
| `talosctl health -n IP` | Check cluster health |
| `talosctl dashboard -n IP` | Interactive node dashboard |
| `talosctl get disks --insecure -n IP` | List disks on node |
| `talosctl get links --insecure -n IP` | List network interfaces |
| `talosctl cluster create docker` | Local Docker cluster |
| `talosctl cluster destroy` | Destroy local cluster |
