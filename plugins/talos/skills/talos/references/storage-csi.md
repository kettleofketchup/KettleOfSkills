# Talos Storage: Rook-Ceph & CSI Drivers Reference

## Rook-Ceph

**Prerequisites**: multiple disks per node (Talos reserves one for OS). Disks must have no partitions/filesystems. K8s 1.16+, Helm 3+.

```bash
helm repo add rook-release https://charts.rook.io/release
helm install --create-namespace --namespace rook-ceph rook-ceph rook-release/rook-ceph
kubectl label namespace rook-ceph pod-security.kubernetes.io/enforce=privileged
helm install --create-namespace --namespace rook-ceph rook-ceph-cluster \
  --set operatorNamespace=rook-ceph rook-release/rook-ceph-cluster
```

StorageClasses created automatically:
- `ceph-block` (rook-ceph.rbd.csi.ceph.com) - block storage
- `ceph-filesystem` (rook-ceph.cephfs.csi.ceph.com) - shared filesystem
- `ceph-bucket` (rook-ceph.ceph.rook.io/bucket) - object storage

**Node maintenance**: upgrade one node at a time, wait for HEALTH_OK:
```bash
kubectl -n rook-ceph wait --timeout=1800s \
  --for=jsonpath='{.status.ceph.health}=HEALTH_OK' cephclusters.ceph.rook.io rook-ceph
```

Use UserVolumeConfig with `type: disk` to dedicate raw disks to Ceph OSDs.

## CSI Drivers Overview

| Driver | Notes |
|--------|-------|
| **Rook/Ceph** | Enterprise distributed storage (RBD, CephFS, S3) |
| **Longhorn** | Simple replicated storage with snapshots |
| **OpenEBS Mayastor** | NVMEoF, ultra-low latency. Disable initContainers + lvm/zfs |
| **Piraeus/LINSTOR** | DRBD-based replication |
| **NFS** | Supported via kubelet image. Avoid multi-mount |
| **iSCSI** | Requires iscsi-tools system extension |

Always use separate disks from Talos install disk. Avoid multi-mount for reliability.

Mayastor Helm values:
```yaml
mayastor:
  csi:
    node:
      initContainers:
        enabled: false
engines:
  local:
    lvm:
      enabled: false
    zfs:
      enabled: false
```
