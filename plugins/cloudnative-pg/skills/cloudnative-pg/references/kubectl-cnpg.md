# kubectl cnpg Plugin

## Install

```bash
curl -sSfL https://github.com/cloudnative-pg/cloudnative-pg/raw/main/hack/install-cnpg-plugin.sh | sudo sh -s -- -b /usr/local/bin
```

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Cluster status (add `-v -v` for config/HBA/certs) | `kubectl cnpg status mydb -n databases` |
| `promote` | Promote replica to primary | `kubectl cnpg promote mydb mydb-2` |
| `restart` | Rolling restart (cluster or single instance) | `kubectl cnpg restart mydb` |
| `reload` | Reload PostgreSQL config without restart | `kubectl cnpg reload mydb` |
| `hibernate` | Suspend cluster, keep PVCs | `kubectl cnpg hibernate on mydb` |
| `hibernate off` | Wake hibernated cluster | `kubectl cnpg hibernate off mydb` |
| `maintenance set` | Enable maintenance mode | `kubectl cnpg maintenance set mydb` |
| `backup` | Trigger manual backup | `kubectl cnpg backup mydb` |
| `destroy` | Remove instance + PVCs | `kubectl cnpg destroy mydb mydb-3` |
| `certificate` | Generate TLS cert for cluster user | `kubectl cnpg certificate mydb --cnpg-user app` |
| `pgbench` | Run pgbench benchmark | `kubectl cnpg pgbench mydb -- --time 30 --client 1` |
| `fio` | Storage I/O benchmark | `kubectl cnpg fio mydb` |
| `logs` | Retrieve cluster logs | `kubectl cnpg logs cluster mydb` |
| `report` | Bundle diagnostics into ZIP | `kubectl cnpg report cluster mydb` |

## Status Output

```bash
# Basic status
kubectl cnpg status mydb -n databases

# Verbose (includes PG config, HBA rules, cert details)
kubectl cnpg status mydb -n databases -v -v

# For large clusters (>1TB), increase timeout
kubectl cnpg status mydb -n databases --timeout 60
```

## Common Workflows

### Manual failover
```bash
# Promote a specific replica
kubectl cnpg promote mydb mydb-2 -n databases
```

### Save resources (homelab)
```bash
# Hibernate -- stops pods, keeps PVCs
kubectl cnpg hibernate on mydb -n databases

# Wake up later
kubectl cnpg hibernate off mydb -n databases
```

### Pre-maintenance benchmark
```bash
# Storage benchmark
kubectl cnpg fio mydb -n databases

# Database benchmark
kubectl cnpg pgbench mydb -n databases -- --time 30 --client 4 --jobs 2
```

### Diagnostics ZIP
```bash
# Cluster report
kubectl cnpg report cluster mydb -n databases -f report.zip

# Operator report
kubectl cnpg report operator -f operator-report.zip
```

## Key Points

- `status` runs filesystem ops on pod (`du`, `cat`) -- slow on large data volumes
- `snapshot` command removed; use `backup` for volume snapshot backups
- Fenced instances cannot be hibernated
- Output supports `yaml` and `json` for scripting: `kubectl cnpg status mydb -o json`
