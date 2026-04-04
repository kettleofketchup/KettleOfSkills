# Troubleshooting

## Quick Diagnostics

```bash
# Cluster status (first thing to check)
kubectl cnpg status mydb -n databases

# Verbose status (PG config, HBA, certs)
kubectl cnpg status mydb -n databases -v -v

# Pod status
kubectl get pods -l cnpg.io/clusterName=mydb -n databases -L role -o wide

# Cluster resource
kubectl get cluster mydb -n databases -o yaml

# Events
kubectl get events -n databases --sort-by=.lastTimestamp | grep mydb
```

## Log Access

```bash
# Instance logs (pretty formatted)
kubectl cnpg logs cluster mydb -n databases

# Operator logs
kubectl logs -n cnpg-system deployment/cnpg-controller-manager --all-containers=true

# Raw pod logs (JSON format)
kubectl logs mydb-1 -n databases
```

Use `jq` for filtering: `kubectl logs mydb-1 -n databases | jq -r 'select(.level=="error")'`

## Common Issues

### CrashLoopBackOff (full disk)

Increase PVC size in Cluster spec (requires StorageClass with `allowVolumeExpansion: true`):

```yaml
spec:
  storage:
    size: 20Gi  # Increase from previous value
```

### Replication Lag

```bash
# Check replication status
kubectl cnpg status mydb -n databases
# Look for "Replication Lag" in output

# Detailed replication info
kubectl exec mydb-1 -n databases -- psql -U postgres -c "SELECT * FROM pg_stat_replication;"
```

Common causes: slow storage, network issues, high write load, insufficient resources.

### Backup Failures

```bash
# Check backup status
kubectl get backup -n databases
kubectl describe backup <backup-name> -n databases

# Check WAL archiving
kubectl cnpg status mydb -n databases
# Look for "WAL archiving" section

# Check Barman Cloud Plugin logs (if using plugin)
kubectl logs -n cnpg-system -l app.kubernetes.io/name=barman-cloud-plugin
```

Common causes: wrong S3 credentials, missing `endpointCA` for self-signed certs, network policy blocking object store.

### Connection Issues

```bash
# Verify services exist
kubectl get svc -n databases | grep mydb

# Test connectivity from within cluster
kubectl run psql-test --rm -it --image=postgres:17 -- psql "host=mydb-rw.databases.svc dbname=app user=app"

# Check pg_hba rules
kubectl cnpg status mydb -n databases -v -v
```

### Network Policies Blocking Operator

```bash
kubectl get networkpolicies -n databases
kubectl get networkpolicies -n cnpg-system
```

Operator needs connectivity to all managed pods. Check for policies blocking port 8000 (instance manager) and 5432 (PostgreSQL).

## Emergency Logical Backup

If continuous backup is broken, take emergency dump:

```bash
kubectl exec mydb-1 -n databases -- pg_dump -U postgres -Fc myapp > emergency-backup.dump
```

## Diagnostic Report

Bundle everything for support:

```bash
kubectl cnpg report cluster mydb -n databases -f cluster-report.zip
kubectl cnpg report operator -f operator-report.zip
```
