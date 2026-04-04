# Talos Upgrades & Maintenance Reference

## Talos OS Upgrade

```bash
talosctl upgrade --nodes <IP> --image ghcr.io/siderolabs/installer:v1.12.x
```

- A/B image scheme: previous kernel+OS preserved for automatic rollback on boot failure
- `--stage` — stage to disk, reboot, apply on boot (use when unmount/file-lock issues block upgrade)
- `--wait` — observe progress; add `--debug` for kernel logs
- `talosctl dmesg -f` — live monitor upgrade on node
- Match `talosctl` binary version to running cluster version
- Upgrade path: latest patch of each intermediate minor (v1.0->v1.0.6->v1.1.2->v1.2.4; never skip minor)
- Sequence: cordon->drain->stop services->unmount fs->verify disk->write image->bootloader->reboot->verify->rejoin->uncordon

### Protections & Pre-Upgrade Checks

- CP nodes: refuses upgrade if etcd quorum would be lost; concurrent CP upgrades serialized
- Workloads needing graceful shutdown: add `lifecycle.preStop` to pod spec
- Verify health: `talosctl health`
- Confirm etcd: `talosctl -n <CPs> etcd status`
- Backup etcd: `talosctl -n <CP> etcd snapshot db.snapshot`
- OS upgrade does NOT upgrade K8s — separate procedure

### Rollback

```bash
talosctl rollback --nodes <IP>
```

Reverts boot reference to previous Talos version, reboots.

## Kubernetes Upgrade

```bash
talosctl --nodes <CP_IP> upgrade-k8s --to 1.x.y
talosctl --nodes <CP_IP> upgrade-k8s --to 1.x.y --dry-run   # preview only
```

- Targets one CP node, applies cluster-wide. Non-disruptive from Talos; kubelet may restart workloads
- Safe to restart on failure — resumes from failure point
- `--dry-run` preview changes + deprecated resources
- `--*-image` override component images (e.g., `--kube-apiserver-image`)
- `--manifests-no-prune` disable resource pruning (v1.13+)

### Automated Phases

1. Pre-pull images on all nodes
2. Patch CP static pod manifests (apiserver, controller-manager, scheduler)
3. Update kube-proxy DaemonSet
4. Upgrade kubelet on all nodes
5. Reapply bootstrap manifests (CoreDNS etc.)
6. Prune removed resources (v1.13+)

### Manual K8s Upgrade (per-component)

```bash
# API server (repeat for controller-manager, scheduler)
talosctl -n <IP> patch mc --mode=no-reboot -p \
  '[{"op":"replace","path":"/cluster/apiServer/image","value":"registry.k8s.io/kube-apiserver:v1.x.y"}]'
# Verify
kubectl get pod -n kube-system -l k8s-app=kube-apiserver --field-selector spec.nodeName=<node>
# kubelet on each node
talosctl -n <IP> patch mc --mode=no-reboot -p \
  '[{"op":"replace","path":"/machine/kubelet/image","value":"ghcr.io/siderolabs/kubelet:v1.x.y"}]'
# Bootstrap manifests — export, diff, apply
talosctl -n <IP> get manifests -o yaml | yq eval-all '.spec | .[] | splitDoc' - > manifests.yaml
kubectl diff -f manifests.yaml && kubectl apply -f manifests.yaml
```

## etcd Maintenance

### Status, Alarms, Defrag

```bash
talosctl -n <CP1>,<CP2>,<CP3> etcd status    # DB size, in-use, leader, RAFT index/term
talosctl -n <IP> etcd alarm list              # check NOSPACE alarms
talosctl etcd alarm disarm                    # clear alarms after quota increase
talosctl -n <IP> etcd defrag                  # blocks r/w; one node at a time; trigger when in-use/size < 0.5
```

### Space Quota (default 2 GiB, max recommended 8 GiB)

```yaml
cluster:
  etcd:
    extraArgs:
      quota-backend-bytes: 4294967296  # 4 GiB
```

Reboot required; then `talosctl etcd alarm disarm`.

### etcd Downgrade (single minor only, e.g., v3.6->v3.5)

```bash
talosctl -n <IP> etcd downgrade validate 3.5   # verify path
talosctl -n <IP> etcd downgrade enable 3.5     # enable
talosctl -n <IP> etcd forfeit-leadership        # before downgrading leader
talosctl -n <IP> patch machineconfig --patch @etcd-patch.yaml --mode reboot
```

Downgrade leader last. Confirm all members' storage version matches before next node.

## Disaster Recovery

### Backup

```bash
talosctl -n <CP_IP> etcd snapshot db.snapshot                      # any healthy CP; schedule regularly
talosctl -n <CP_IP> cp /var/lib/etcd/member/snap/db .              # raw copy when quorum lost
talosctl -n <IP> get mc v1alpha1 -o yaml | yq eval '.spec' -      # machine config backup
```

### Recovery from Snapshot

Prerequisites: confirm quorum unrecoverable (`talosctl -n <IP> etcd members` + `talosctl -n <IP> service etcd`). Convert `init` type to `controlplane` via `talosctl edit mc --mode=staged`.

```bash
# 1. Reset all CP nodes (preserve boot, wipe ephemeral)
talosctl -n <CP1>,<CP2>,<CP3> reset --graceful=false --reboot \
  --system-labels-to-wipe=EPHEMERAL
# 2. Wait for all CP etcd services to reach "Preparing" state
# 3. Bootstrap from snapshot on one CP node
talosctl -n <CP1> bootstrap --recover-from=./db.snapshot
# For raw DB copies:
talosctl -n <CP1> bootstrap --recover-from=./db --recover-skip-hash-check
```

Remaining CP nodes rejoin automatically. Single-node: snapshot regularly -- no recovery without backup.

## Scaling Up (Add Nodes)

Requires original `controlplane.yaml` / `worker.yaml` (contain cluster PKI certs).

```bash
talosctl apply-config --insecure --nodes <NEW_IP> --file worker.yaml
talosctl apply-config --insecure --nodes <NEW_IP> --file controlplane.yaml
```

`--insecure` required (PKI not yet on node). No bootstrap needed; nodes auto-join in assigned role.

## Scaling Down (Remove Nodes)

```bash
talosctl -n <IP_TO_REMOVE> reset
kubectl delete node <nodename>
```

Both steps mandatory. Reset: cordon->drain->leave etcd (if CP)->erase disks->shutdown->deregister from discovery. Same procedure for CP and worker nodes.

## Machine Reset

```bash
talosctl reset -n <IP>
```

| Flag | Effect | Default |
|------|--------|---------|
| `--graceful` | cordon/drain, leave etcd cleanly | true |
| `--reboot` | reboot after reset instead of shutdown | false |
| `--system-labels-to-wipe` | selective partition wipe (repeatable) | all |

```bash
talosctl reset -n <IP> --graceful=true                              # HA cluster
talosctl reset -n <IP> --graceful=false                             # single-node / broken etcd
talosctl reset -n <IP> --system-labels-to-wipe STATE \
  --system-labels-to-wipe EPHEMERAL                                 # cloud VMs (preserve boot)
# Unresponsive node — kernel param via GRUB: talos.experimental.wipe=system
```

WARNING: full disk wipe on cloud VMs without iPXE renders VM unbootable.

## Workloads on Control Plane

```yaml
cluster:
  allowSchedulingOnControlPlanes: true
```

Removes default CP taints. Apply in `controlplane.yaml` or patch live. Useful for single-node/non-prod.

### Allow CP nodes in external load balancers (e.g., MetalLB)

```yaml
machine:
  nodeLabels:
    node.kubernetes.io/exclude-from-external-load-balancers:
      $patch: delete
```
