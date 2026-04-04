# PgBouncer Connection Pooling

CNPG provides native PgBouncer via the `Pooler` CRD. Creates a separate deployment of PgBouncer pods between apps and PostgreSQL.

## Basic Pooler

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: myapp-db-pooler-rw
  namespace: databases
spec:
  cluster:
    name: myapp-db
  instances: 2
  type: rw  # rw for primary, ro for replicas

  pgbouncer:
    poolMode: transaction
    parameters:
      default_pool_size: "25"
      max_client_conn: "200"
      max_db_connections: "0"
      log_connections: "1"
      log_disconnections: "1"
```

## Read-Only Pooler

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: myapp-db-pooler-ro
  namespace: databases
spec:
  cluster:
    name: myapp-db
  instances: 2
  type: ro  # Points to replica instances

  pgbouncer:
    poolMode: transaction
    parameters:
      default_pool_size: "25"
      max_client_conn: "200"
```

## Pool Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `transaction` | Connection returned after transaction | Most web apps (recommended) |
| `session` | Connection held for entire session | Apps using session features (LISTEN/NOTIFY, prepared statements) |
| `statement` | Connection returned after each statement | Simple queries only (no multi-statement txns) |

## Connect via Pooler

Applications connect to the Pooler service instead of the Cluster service:

```
host=myapp-db-pooler-rw.databases.svc dbname=myapp user=myapp
host=myapp-db-pooler-ro.databases.svc dbname=myapp user=myapp
```

## Key Points

- Pooler is a separate resource, NOT auto-deleted with the Cluster
- Deploy multiple Poolers per cluster (e.g., one RW, one RO)
- Only password-based auth for PgBouncer clients
- PgBouncer uses TLS client certs internally to connect to PostgreSQL
- TLS handled transparently on both sides
- Operator manages PgBouncer config, certs, and `auth_query` automatically
- Scale PgBouncer independently by changing `instances`

## Common Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `default_pool_size` | 20 | Server connections per user/database pair |
| `max_client_conn` | 100 | Max client connections |
| `max_db_connections` | 0 | Max connections per database (0 = unlimited) |
| `reserve_pool_size` | 0 | Extra connections for burst |
| `reserve_pool_timeout` | 5 | Seconds before using reserve pool |
