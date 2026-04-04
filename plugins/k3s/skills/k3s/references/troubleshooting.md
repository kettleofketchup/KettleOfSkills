# K3s Troubleshooting

## Service Status & Logs

```bash
# Service status
systemctl status k3s              # Server
systemctl status k3s-agent        # Agent

# Journal logs
journalctl -u k3s -f              # Follow server logs
journalctl -u k3s-agent -f        # Follow agent logs
journalctl -u k3s --since "10 min ago"

# Containerd logs
cat /var/lib/rancher/k3s/agent/containerd/containerd.log
```

## Common Issues

### Node stuck NotReady

Usually CNI not installed or not running:
```bash
kubectl describe node <name>       # Check conditions
kubectl get pods -n kube-system    # Check CNI pods
kubectl get pods -n tigera-operator  # If using Calico
```

Fix: Ensure CNI is deployed. If using custom CNI, verify `--flannel-backend=none` is set.

### Pods stuck ImagePullBackOff (airgap)

Images not pre-loaded or wrong `imagePullPolicy`:
```bash
# Check which images are loaded
crictl --runtime-endpoint unix:///run/k3s/containerd/containerd.sock images

# Manually import an image
ctr -n k8s.io image import /path/to/image.tar

# Check image directory
ls -la /var/lib/rancher/k3s/agent/images/
```

### K3s fails to start

```bash
# Check for port conflicts
ss -tlnp | grep -E '6443|10250|8472'

# Check disk space (etcd needs space)
df -h /var/lib/rancher/k3s/

# Verify binary
k3s --version
k3s check-config   # Validate system prerequisites
```

### etcd issues (HA)

```bash
# Check etcd member list
k3s etcd-snapshot list

# Check etcd health via API
curl -sL https://localhost:2379/health --cacert /var/lib/rancher/k3s/server/tls/etcd/server-ca.crt \
  --cert /var/lib/rancher/k3s/server/tls/etcd/server-client.crt \
  --key /var/lib/rancher/k3s/server/tls/etcd/server-client.key

# Defrag (if etcd db too large)
k3s etcd-snapshot save  # backup first
```

### Cannot reach API server

```bash
# Verify kubeconfig
cat /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl cluster-info

# Check API server is listening
curl -sk https://localhost:6443/healthz

# For remote access, ensure --tls-san includes the access IP
```

### Containerd / crictl

```bash
# K3s bundles its own containerd and crictl
export CRI_CONFIG_FILE=/var/lib/rancher/k3s/agent/etc/crictl.yaml

# Or use K3s built-in crictl
k3s crictl ps                      # List running containers
k3s crictl images                  # List loaded images
k3s crictl logs <container-id>     # Container logs
k3s crictl inspect <container-id>  # Container details
```

### Registry / Pull Issues

```bash
# Verify registries.yaml is valid
cat /etc/rancher/k3s/registries.yaml

# Check generated containerd config
cat /var/lib/rancher/k3s/agent/etc/containerd/config.toml

# Test registry connectivity
curl -sk https://registry.local:5000/v2/_catalog

# Containerd pull logs
grep -i "pull\|registry\|auth" /var/lib/rancher/k3s/agent/containerd/containerd.log
```

### Networking / CNI Issues

```bash
# Check CNI config
ls /etc/cni/net.d/
cat /etc/cni/net.d/10-calico.conflist  # If Calico

# Check pod networking
kubectl run test --image=busybox --rm -it -- wget -qO- http://kubernetes.default.svc

# Check flannel/calico pods
kubectl get pods -n kube-system -l k8s-app=calico-node
kubectl get pods -n kube-system -l app=flannel

# VXLAN interface
ip link show flannel.1   # Flannel
ip link show vxlan.calico  # Calico VXLAN
```

## Diagnostic Commands

```bash
# Full system check
k3s check-config

# Cluster status
kubectl get nodes -o wide
kubectl get cs                     # Component status
kubectl top nodes                  # Resource usage

# All pods across namespaces
kubectl get pods -A -o wide

# Events (recent issues)
kubectl get events -A --sort-by='.lastTimestamp' | tail -20
```

## Reset / Uninstall

```bash
# Full uninstall (server)
/usr/local/bin/k3s-uninstall.sh

# Full uninstall (agent)
/usr/local/bin/k3s-agent-uninstall.sh

# These scripts:
# - Stop service
# - Remove binary, scripts, data
# - Clean iptables/ipvs rules
# - Remove CNI config
```

## NixOS-Specific

On NixOS, K3s is managed via systemd + Nix config. Common patterns:
```bash
# Restart K3s (NixOS)
systemctl restart k3s

# Rebuild with changes
nixos-rebuild switch

# Check NixOS-generated K3s service
systemctl cat k3s
```
