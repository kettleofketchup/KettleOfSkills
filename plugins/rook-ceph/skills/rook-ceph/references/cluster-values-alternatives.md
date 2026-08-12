# Cluster Values: Alternative Configurations

## Object Store (S3-Compatible)

Add to `cluster-values.yaml` to enable S3-compatible object storage:

```yaml
cephObjectStores:
  - name: objectstore
    spec:
      metadataPool:
        failureDomain: host
        replicated:
          size: 3
      dataPool:
        failureDomain: host
        replicated:
          size: 3
      gateway:
        port: 80
        instances: 2
    storageClass:
      enabled: true
      name: ceph-bucket
      reclaimPolicy: Delete
```

## Use All Devices

For clusters where all nodes contribute storage automatically:

```yaml
cephClusterSpec:
  mon:
    count: 3
    allowMultiplePerNode: false
  mgr:
    count: 2
    allowMultiplePerNode: false
  placement:
    all:
      nodeAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
          nodeSelectorTerms:
            - matchExpressions:
                - key: ceph-node
                  operator: In
                  values:
                    - "true"
  storage:
    useAllNodes: true
    useAllDevices: true
    deviceFilter: "^sd[b-z]"  # Only use sdb, sdc, etc.
```

## Label Nodes

Before deploying, label each node that should participate in the Ceph cluster:

```bash
kubectl label node node1 ceph-node=true
kubectl label node node2 ceph-node=true
kubectl label node node3 ceph-node=true
```

To verify labels:

```bash
kubectl get nodes --show-labels | grep ceph-node
```

To remove a node from Ceph (before removing its label, drain OSDs first):

```bash
# Remove OSDs on the node before unlabeling
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- ceph osd out <osd-id>
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- ceph osd purge <osd-id> --yes-i-really-mean-it

# Then remove the label
kubectl label node <name> ceph-node-
```
