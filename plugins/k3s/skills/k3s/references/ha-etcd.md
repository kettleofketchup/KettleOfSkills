# K3s HA with Embedded etcd

## Overview

K3s supports HA via embedded etcd (no external DB needed). Requires **odd number of server nodes** (3, 5, 7) for quorum: `(n/2)+1` nodes must be healthy.

| Servers | Quorum | Fault Tolerance |
|---------|--------|-----------------|
| 1 | 1 | 0 (no HA) |
| 3 | 2 | 1 node failure |
| 5 | 3 | 2 node failures |

## Initialize First Server

```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET sh -s - server \
    --cluster-init \
    --tls-san=<FIXED_IP_OR_LB>
```

`--tls-san` adds a SAN to the API server cert — use a load balancer VIP or DNS name that won't change.

## Join Additional Servers

```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET sh -s - server \
    --server https://<FIRST_SERVER>:6443 \
    --tls-san=<FIXED_IP_OR_LB>
```

Verify:
```bash
kubectl get nodes
# NAME      STATUS   ROLES                       AGE   VERSION
# server1   Ready    control-plane,etcd,master   28m   vX.Y.Z
# server2   Ready    control-plane,etcd,master   13m   vX.Y.Z
# server3   Ready    control-plane,etcd,master   10m   vX.Y.Z
```

## Join Agent Nodes

```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET sh -s - agent \
    --server https://<SERVER_OR_LB>:6443
```

## Critical: Flag Consistency

These flags **must be identical across all servers**:
- `--cluster-cidr`, `--service-cidr`, `--cluster-dns`, `--cluster-domain`
- `--flannel-backend`, `--disable-network-policy`
- `--disable-helm-controller`, `--disable-kube-proxy`
- `--secrets-encryption`

Mismatches cause validation errors; nodes fail to join.

## etcd Snapshots

### Automatic (default)

K3s takes periodic snapshots. Configure:

```yaml
# /etc/rancher/k3s/config.yaml
etcd-snapshot-schedule-cron: "0 */6 * * *"   # Every 6 hours
etcd-snapshot-retention: 10                    # Keep 10 snapshots
etcd-snapshot-dir: /var/lib/rancher/k3s/server/db/snapshots
```

### S3 Backup

```yaml
etcd-s3: true
etcd-s3-bucket: k3s-backups
etcd-s3-region: us-east-1
etcd-s3-endpoint: s3.amazonaws.com
etcd-s3-access-key: AKIA...
etcd-s3-secret-key: ...
```

### Manual Snapshot

```bash
k3s etcd-snapshot save --name pre-upgrade
k3s etcd-snapshot list
k3s etcd-snapshot delete <name>
```

## Restore from Snapshot

**Stop K3s on ALL server nodes first**, then restore on ONE node:

```bash
# On one server:
k3s server --cluster-reset --cluster-reset-restore-path=/path/to/snapshot.db

# After reset completes, restart K3s normally
systemctl start k3s

# On other servers: delete data and rejoin
rm -rf /var/lib/rancher/k3s/server/db/
systemctl start k3s
```

## Single-Node to HA Migration

Existing SQLite single-node clusters can migrate to embedded etcd:

```bash
# Restart existing single server with:
k3s server --cluster-init
# Then join additional servers normally
```

## External Datastore (alternative)

Instead of embedded etcd, use MySQL/PostgreSQL/etcd:

```bash
K3S_DATASTORE_ENDPOINT='mysql://user:pass@tcp(host:3306)/k3s' \
  k3s server
```

Supported: MySQL 5.7+, PostgreSQL 10+, external etcd 3.5+, NATS (experimental).

## HA Load Balancer

Place a TCP load balancer in front of server nodes on port 6443. Options:
- HAProxy / Nginx (L4 TCP passthrough)
- Keepalived VIP
- Cloud LB (if not airgapped)

All agents and `kubectl` clients should target the LB address.
