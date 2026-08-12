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

See `references/getting-started-production.md` for HA 3-control-plane setup.
