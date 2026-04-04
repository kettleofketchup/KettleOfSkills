# Operations

## Failover (Automatic)

When primary becomes unhealthy, operator auto-promotes most up-to-date replica.

```yaml
spec:
  failoverDelay: 0  # Seconds to wait before failover (default: 0 = immediate)
```

- Set non-zero `failoverDelay` if experiencing frequent short-lived network blips
- Operator uses `pg_rewind` to re-sync old primary as replica after failover

## Switchover (Planned)

Controlled transfer of primary role to a specific replica.

```bash
kubectl cnpg promote mydb mydb-2 -n databases
```

```yaml
spec:
  switchoverDelay: 3600  # Max seconds for old primary to shut down and archive WAL
```

- Low `switchoverDelay` = faster RTO but risk of data loss
- High value = less data-loss risk but longer without active primary

## Hibernate (Homelab)

Suspend clusters to free resources. PVCs persist.

```bash
# Hibernate
kubectl cnpg hibernate on mydb -n databases

# Wake
kubectl cnpg hibernate off mydb -n databases
```

- Annotation-based: sets `cnpg.io/hibernation=on`
- Fenced instances cannot be hibernated
- Great for homelab -- spin down databases not actively in use

## Maintenance Windows

Control behavior during Kubernetes node maintenance.

```yaml
spec:
  nodeMaintenanceWindow:
    inProgress: true     # Set when starting node maintenance
    reusePVC: true       # Wait for node to return, reuse PVC (recommended)
```

| `reusePVC` | Behavior |
|------------|----------|
| `true` | Wait for node return, reattach PVC. PDB temporarily removed. |
| `false` | Recreate pod on different node with new PVC via streaming replication. |

- Single-instance clusters with `reusePVC: false` will be **blocked** (would lose all data)
- Use `kubectl cnpg maintenance set` to apply across clusters/namespaces

## Rolling Updates

```yaml
spec:
  primaryUpdateStrategy: unsupervised  # or 'supervised' for manual primary update
  primaryUpdateMethod: switchover      # or 'restart'
```

- `unsupervised`: replicas updated first, then primary switchover (fully automatic)
- `supervised`: replicas updated, primary requires manual intervention

## Database Import

Import existing PostgreSQL into CNPG via logical backup (pg_dump/pg_restore).

### Microservice (single database)

```yaml
spec:
  bootstrap:
    initdb:
      import:
        type: microservice
        databases:
          - source_db
        source:
          externalClusterName: source-pg
  externalClusters:
    - name: source-pg
      connectionParameters:
        host: old-postgres.example.com
        user: postgres
        dbname: source_db
      password:
        name: source-pg-password
        key: password
```

### Monolith (multiple databases + roles)

```yaml
spec:
  bootstrap:
    initdb:
      import:
        type: monolith
        databases:
          - db1
          - db2
        roles:
          - role1
          - role2
        source:
          externalClusterName: source-pg
```

| Feature | Microservice | Monolith |
|---------|-------------|----------|
| Databases | Exactly 1 | Multiple |
| Roles imported | No | Yes |
| DB renamed | To `app` (or initdb value) | Preserved |

## Scaling

```bash
# Scale replicas (edit instances count)
kubectl patch cluster mydb -n databases --type merge -p '{"spec":{"instances":3}}'
```

- Scale up: new replicas join via streaming replication
- Scale down: operator removes replicas (not primary)
