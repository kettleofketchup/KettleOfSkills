# Talos Maintenance Reference

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
