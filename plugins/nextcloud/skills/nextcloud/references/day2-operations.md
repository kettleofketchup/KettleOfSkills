# Nextcloud Day-2 Operations

## occ Command Reference

All occ commands must run as `www-data` user:

```bash
NEXTCLOUD_POD=$(kubectl get pod -n nextcloud -l app.kubernetes.io/name=nextcloud -o jsonpath='{.items[0].metadata.name}')
OCC="kubectl exec -n nextcloud $NEXTCLOUD_POD -- su -s /bin/sh www-data -c"

# Status
$OCC "php occ status"
$OCC "php occ app:list"
$OCC "php occ user:list"

# Maintenance mode
$OCC "php occ maintenance:mode --on"
$OCC "php occ maintenance:mode --off"

# Database maintenance (run after upgrades)
$OCC "php occ db:add-missing-indices"
$OCC "php occ db:add-missing-columns"
$OCC "php occ db:add-missing-primary-keys"
$OCC "php occ maintenance:repair"

# File operations
$OCC "php occ files:scan --all"
$OCC "php occ files:cleanup"

# Config management
$OCC "php occ config:system:get trusted_domains"
$OCC "php occ config:system:set trusted_domains 2 --value=new.domain.com"
$OCC "php occ config:list system"

# User management
$OCC "php occ user:setting admin email admin@example.com"
$OCC "php occ user:disable <username>"
$OCC "php occ user:enable <username>"
```

## Upgrades

**Nextcloud only supports sequential major version upgrades.**

### Pre-Upgrade Checklist

1. Back up PostgreSQL database
2. Back up Nextcloud data PVC
3. Check current version: `$OCC "php occ status"`
4. Verify target version is next sequential major (e.g., 29→30, NOT 29→31)
5. Check app compatibility with target version

### Upgrade Process

```bash
# 1. Enable maintenance mode
$OCC "php occ maintenance:mode --on"

# 2. Back up database
DB_POD=$(kubectl get pod -n nextcloud -l app.kubernetes.io/name=postgresql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n nextcloud $DB_POD -- pg_dump -U nextcloud nextcloud > nextcloud-backup-$(date +%Y%m%d).sql

# 3. Update Helm values with new image tag or chart version
# Edit values.yaml, then sync via ArgoCD or helm upgrade

# 4. After pod restarts, run post-upgrade tasks
$OCC "php occ db:add-missing-indices"
$OCC "php occ db:add-missing-columns"
$OCC "php occ maintenance:repair"

# 5. Disable maintenance mode
$OCC "php occ maintenance:mode --off"

# 6. Verify
$OCC "php occ status"
```

### Rollback

If upgrade fails:
1. Restore database from backup
2. Revert Helm values to previous chart version
3. Sync/upgrade to restore old version
4. Disable maintenance mode

## Backups

### Database Backup (PostgreSQL)

```bash
# One-time backup
DB_POD=$(kubectl get pod -n nextcloud -l app.kubernetes.io/name=postgresql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n nextcloud $DB_POD -- pg_dump -U nextcloud nextcloud > nextcloud-db-$(date +%Y%m%d).sql

# Restore
cat nextcloud-db-backup.sql | kubectl exec -i -n nextcloud $DB_POD -- psql -U nextcloud nextcloud
```

### Data Backup (PVC)

For Rook-Ceph, use VolumeSnapshots:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: nextcloud-data-snap
  namespace: nextcloud
spec:
  volumeSnapshotClassName: ceph-block-snapshot
  source:
    persistentVolumeClaimName: nextcloud-nextcloud-data
```

## Troubleshooting

### "Access through untrusted domain"
Add pod/node CIDRs to `trusted_proxies` in Helm values and set trusted domains via occ:
```bash
$OCC "php occ config:system:set trusted_domains 2 --value=cloud.example.com"
```

### Pod CrashLoopBackOff After Upgrade
Likely skipped a major version. Restore backup, upgrade sequentially. Check for stuck maintenance mode in `config/config.php`.

### Redis Connection Errors
```bash
kubectl exec -n nextcloud $NEXTCLOUD_POD -- redis-cli -h nextcloud-redis-master -a <password> ping
```

### Cron Not Running
```bash
kubectl get pod -n nextcloud -o jsonpath='{.items[0].spec.containers[*].name}'
$OCC "php occ config:app:get core lastcron"
```

### Collabora "WOPI Host Not Allowed"
Verify `collabora.collabora.aliasgroups[0].host` matches Nextcloud external URL exactly.
Check logs: `kubectl logs -n nextcloud -l app.kubernetes.io/name=collabora`
