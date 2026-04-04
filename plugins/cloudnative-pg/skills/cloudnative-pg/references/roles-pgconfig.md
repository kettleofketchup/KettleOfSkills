# Declarative Roles and PostgreSQL Configuration

## Declarative Role Management

Manage PostgreSQL roles via Cluster spec. Operator continuously reconciles.

```yaml
spec:
  managed:
    roles:
      - name: readonly_user
        ensure: present
        login: true
        superuser: false
        createdb: false
        inRoles:
          - pg_read_all_data
        passwordSecret:
          name: readonly-user-password

      - name: admin_user
        ensure: present
        login: true
        createdb: true
        createrole: true
        passwordSecret:
          name: admin-user-password

      - name: old_user
        ensure: absent  # Will be dropped
```

### Password Secret Format

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: readonly-user-password
  namespace: databases
type: kubernetes.io/basic-auth
stringData:
  username: readonly_user  # Must match role name
  password: "secure-password-here"
```

### Role Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| `login` | false | Can log in |
| `superuser` | false | Superuser privileges |
| `createdb` | false | Can create databases |
| `createrole` | false | Can create roles |
| `inherit` | true | Inherits privileges of roles it belongs to |
| `replication` | false | Can initiate replication |
| `bypassrls` | false | Bypass row-level security |
| `connectionLimit` | -1 | Max connections (-1 = unlimited) |
| `inRoles` | [] | Role memberships |
| `disablePassword` | false | Set password to NULL |

### Key Points

- Manual SQL changes to managed roles are **reverted** on next reconciliation
- `postgres` and `streaming_replica` are **reserved** -- cannot be managed
- `cannotReconcile` status requires manual intervention
- `validUntil` unset = password never expires

## PostgreSQL Configuration

All config via Cluster spec, uniform across all instances.

```yaml
spec:
  postgresql:
    parameters:
      # Memory
      shared_buffers: "256MB"
      effective_cache_size: "768MB"
      work_mem: "8MB"
      maintenance_work_mem: "128MB"

      # Connections
      max_connections: "200"

      # WAL
      wal_buffers: "8MB"
      min_wal_size: "80MB"
      max_wal_size: "1GB"

      # Logging (most log settings are fixed by CNPG)
      log_min_duration_statement: "1000"  # Log queries > 1s

      # Extensions
      # shared_preload_libraries auto-managed for known extensions

    pg_hba:
      - host all all 10.0.0.0/8 md5  # Allow from cluster network
```

### Fixed/Immutable Settings

- Log format settings are fixed (CSV output, parsed to JSON by instance manager)
- ALTER SYSTEM disabled by default
- Hot standby settings managed by operator
- `shared_preload_libraries` auto-managed for known extensions; add custom entries only if needed

### LDAP Authentication

```yaml
spec:
  postgresql:
    ldap:
      server: ldap.example.com
      bindSearchAuth:
        baseDN: "ou=users,dc=example,dc=com"
        bindDN: "cn=admin,dc=example,dc=com"
        bindPassword:
          name: ldap-bind-secret
          key: password
        searchAttribute: uid
```
