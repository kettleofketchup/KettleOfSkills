# Talos Upgrades Reference

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

See `references/maintenance.md` for etcd maintenance, disaster recovery, and node scaling.
