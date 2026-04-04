# Talos Storage Reference

## Disk Layout

Talos boot disk has 4 partitions (GPT):
- **EFI** ~1GB - boot
- **META** ~1MB - metadata (stores encryption keys for STATE)
- **STATE** ~100MB - machine config, etcd snapshots
- **EPHEMERAL** - remaining space - container images, logs, etcd data

EFI/META/STATE layout is hardcoded. EPHEMERAL can be resized or moved to another disk.

```bash
talosctl get disks
talosctl get discoveredvolumes   # shows all volumes incl. third-party
```

Supported filesystems: ext2/3/4, xfs, vfat, zfs, lvm2, luks, bluestore (Ceph), squashfs, swap.

## Disk Encryption (LUKS2)

Encrypt STATE, EPHEMERAL, or user volumes. Four key types combinable per volume:

| Key Type | Description |
|----------|-------------|
| `static` | Passphrase in config. On STATE, stored cleartext in META (insecure) |
| `nodeID` | Derived from node UUID. No physical-access protection |
| `tpm` | TPM-derived. Strongest with SecureBoot. Bind to PCRs |
| `kms` | Network KMS sealed. Requires network before STATE decrypt |

Encrypted devices map to `/dev/mapper/luks2-<volume-id>`.

```yaml
apiVersion: v1alpha1
kind: VolumeConfig
name: EPHEMERAL
encryption:
  provider: luks2
  keys:
    - nodeID: {}
      slot: 0
    - tpm:
        options:
          pcrs: [0, 7]
      slot: 1
```

`lockToState: true` - bind key to STATE contents; prevents unlock if STATE wiped. Recommended for EPHEMERAL/user volumes.

**Key rotation**: add new key + reboot, remove old key + reboot. LUKS2 supports up to 32 slots.

**Encrypt existing EPHEMERAL**: apply config `--mode=staged`, then `talosctl reset --system-labels-to-wipe EPHEMERAL --reboot=true`.

## User Volumes

Dynamic local storage for K8s workloads. Mount at `/var/mnt/<name>`, label `u-<name>`.

```yaml
apiVersion: v1alpha1
kind: UserVolumeConfig
name: local-volume
provisioning:
  diskSelector:
    match: disk.transport == 'nvme'
  minSize: 100GB
  maxSize: 200GB
```

Apply: `talosctl --nodes <NODE> patch mc --patch @user-volume.patch.yaml`

**Volume types**:
- **partition** (default) - dedicated partition on matched disk
- **disk** - whole block device, no min/maxSize. Selector must use stable ID (WWN/serial)
- **directory** - simple dir on EPHEMERAL, no isolation/encryption

```bash
talosctl get volumestatus u-local-volume
talosctl wipe disk nvme0n1p2 --drop-partition   # remove data
```

Pod usage via hostPath:
```yaml
volumes:
  - name: local-volume
    hostPath:
      path: /var/mnt/local-volume
```

Encryption supported - add `encryption:` block same as VolumeConfig.

## Local Path Provisioner

Deploy Rancher local-path-provisioner on user volumes for dynamic PVC provisioning:

```yaml
# UserVolumeConfig
apiVersion: v1alpha1
kind: UserVolumeConfig
name: local-path-provisioner
provisioning:
  diskSelector:
    match: disk.transport == 'nvme'
  minSize: 200GB
  maxSize: 200GB
```

Kustomization to deploy + configure:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - github.com/rancher/local-path-provisioner/deploy?ref=v0.0.31
patches:
  - patch: |-
      kind: ConfigMap
      data:
        config.json: |-
          {"nodePathMap":[{"node":"DEFAULT_PATH_FOR_NON_LISTED_NODES",
          "paths":["/var/mnt/local-path-provisioner"]}]}
  - patch: |-
      apiVersion: storage.k8s.io/v1
      kind: StorageClass
      metadata:
        name: local-path
        annotations:
          storageclass.kubernetes.io/is-default-class: "true"
```

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
