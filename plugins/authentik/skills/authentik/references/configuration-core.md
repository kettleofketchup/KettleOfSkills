# Authentik Configuration: Core Settings

All settings via environment variables. Double underscore (`__`) separates nested keys.
Values support `env://<name>` and `file://<name>` URI syntax for indirection.

Docs: https://docs.goauthentik.io/install-config/configuration

## Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_SECRET_KEY` | (required) | Cookie/session signing key. Changing invalidates sessions |
| `AUTHENTIK_LOG_LEVEL` | `info` | `debug`, `info`, `warning`, `error`, `trace`. Trace includes sensitive data |
| `AUTHENTIK_COOKIE_DOMAIN` | auto | Session cookie domain |
| `AUTHENTIK_SKIP_MIGRATIONS` | `false` | Skip DB migrations on startup (not recommended) |
| `AUTHENTIK_WEB__BASE_URL` | - | External scheme+host, e.g. `https://authentik.company`. **New in 2026.8, required from 2026.11.** Also settable as `base_url` in **System > Settings** or via the API |
| `AUTHENTIK_BOOTSTRAP_PASSWORD_HASH` | - | Seed `akadmin` with a pre-hashed Django password (2026.5+). Use instead of `AUTHENTIK_BOOTSTRAP_PASSWORD` to keep plaintext out of the environment |

## PostgreSQL

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_POSTGRESQL__HOST` | - | DB hostname (hot-reloadable) |
| `AUTHENTIK_POSTGRESQL__PORT` | `5432` | DB port (hot-reloadable) |
| `AUTHENTIK_POSTGRESQL__USER` | - | DB user (hot-reloadable) |
| `AUTHENTIK_POSTGRESQL__PASSWORD` | - | DB password (hot-reloadable) |
| `AUTHENTIK_POSTGRESQL__NAME` | - | Database name |
| `AUTHENTIK_POSTGRESQL__SSLMODE` | `verify-ca` | `disable`, `allow`, `prefer`, `require`, `verify-ca`, `verify-full` |
| `AUTHENTIK_POSTGRESQL__SSLROOTCERT` | - | CA certificate path |
| `AUTHENTIK_POSTGRESQL__SSLCERT` | - | Client SSL certificate |
| `AUTHENTIK_POSTGRESQL__SSLKEY` | - | Client certificate key |
| `AUTHENTIK_POSTGRESQL__CONN_MAX_AGE` | `0` | Max connection age (seconds) |
| `AUTHENTIK_POSTGRESQL__CONN_HEALTH_CHECKS` | `false` | Enable persistent connection health checks |
| `AUTHENTIK_POSTGRESQL__DISABLE_SERVER_SIDE_CURSORS` | `false` | **Set `true` for PgBouncer transaction mode** |
| `AUTHENTIK_POSTGRESQL__DEFAULT_SCHEMA` | `public` | DB schema (cannot change after init) |
| `AUTHENTIK_POSTGRESQL__CONN_OPTIONS` | - | **Deprecated in 2026.5**, slated for removal |

### Transaction-Mode Pooler + Direct Connection (2026.8+)

Before 2026.8, PgBouncer in transaction mode needed
`DISABLE_SERVER_SIDE_CURSORS=true` and still broke on LISTEN/NOTIFY and advisory
locks. 2026.8 splits the two needs: the primary `AUTHENTIK_POSTGRESQL__*`
settings carry normal traffic and may point at a transaction-mode pooler, while
`AUTHENTIK_POSTGRESQL__DIRECT__*` points at a direct or session-pooled endpoint
used for operations that require a stable session.

| Variable | Description |
|----------|-------------|
| `AUTHENTIK_POSTGRESQL__DIRECT__HOST` | Direct/session-pooled hostname |
| `AUTHENTIK_POSTGRESQL__DIRECT__PORT` | Direct port |
| `AUTHENTIK_POSTGRESQL__DIRECT__NAME` | Database name |
| `AUTHENTIK_POSTGRESQL__DIRECT__USER` | DB user |
| `AUTHENTIK_POSTGRESQL__DIRECT__PASSWORD` | DB password |
| `AUTHENTIK_POSTGRESQL__DIRECT__SSLMODE` | SSL mode |
| `AUTHENTIK_POSTGRESQL__DIRECT__SSLROOTCERT` | CA certificate path |
| `AUTHENTIK_POSTGRESQL__DIRECT__SSLCERT` | Client SSL certificate |
| `AUTHENTIK_POSTGRESQL__DIRECT__SSLKEY` | Client certificate key |

Unset `DIRECT` settings fall back to the primary connection, so deployments
without a pooler need no change.

### Read Replicas

Indexed via `AUTHENTIK_POSTGRESQL__READ_REPLICAS__<index>__<setting>`.
Each replica accepts: `HOST`, `PORT`, `NAME`, `USER`, `PASSWORD`, `SSLMODE`, `SSLROOTCERT`, `SSLCERT`, `SSLKEY`, `CONN_MAX_AGE`, `CONN_HEALTH_CHECKS`, `DISABLE_SERVER_SIDE_CURSORS`.

`AUTHENTIK_POSTGRESQL__REPLICA_CONN_OPTIONS` and the per-replica `CONN_OPTIONS`
are **deprecated as of 2026.5**.

## Cache

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_CACHE__TIMEOUT` | `300` | General cache expiry (seconds) |
| `AUTHENTIK_CACHE__TIMEOUT_FLOWS` | `300` | Flow plan cache expiry |
| `AUTHENTIK_CACHE__TIMEOUT_POLICIES` | `300` | Policy cache expiry |

## Email (SMTP)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_EMAIL__HOST` | `localhost` | SMTP server |
| `AUTHENTIK_EMAIL__PORT` | `25` | SMTP port |
| `AUTHENTIK_EMAIL__USERNAME` | - | SMTP username |
| `AUTHENTIK_EMAIL__PASSWORD` | - | SMTP password |
| `AUTHENTIK_EMAIL__USE_TLS` | `false` | STARTTLS |
| `AUTHENTIK_EMAIL__USE_SSL` | `false` | SSL/TLS |
| `AUTHENTIK_EMAIL__TIMEOUT` | `10` | SMTP timeout (seconds) |
| `AUTHENTIK_EMAIL__FROM` | `authentik@localhost` | Sender address. Format: `Name <addr>` |

## Listen Addresses

| Variable | Default | Applies to |
|----------|---------|------------|
| `AUTHENTIK_LISTEN__HTTP` | `[::]:9000` | Server, Worker, Proxy outposts |
| `AUTHENTIK_LISTEN__HTTPS` | `[::]:9443` | Server, Proxy outposts |
| `AUTHENTIK_LISTEN__LDAP` | `[::]:3389` | LDAP outposts |
| `AUTHENTIK_LISTEN__LDAPS` | `[::]:6636` | LDAP outposts |
| `AUTHENTIK_LISTEN__METRICS` | `[::]:9300` | Prometheus metrics |
| `AUTHENTIK_LISTEN__DEBUG` | `[::]:9900` | Server/outpost debug (Go pre-2026.8, Rust after) |
| `AUTHENTIK_LISTEN__DEBUG_PY` | `[::]:9901` | Python debug |
| `AUTHENTIK_LISTEN__TRUSTED_PROXY_CIDRS` | RFC1918+loopback | Comma-separated CIDRs for proxy headers |

**Breaking change in 2026.5:** the listen default moved from `0.0.0.0` to `[::]`
(dual-stack). IPv4-only environments that can't bind IPv6 must set the values
back explicitly, e.g. `AUTHENTIK_LISTEN__HTTP=0.0.0.0:9000`.

## Web Server (Gunicorn)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_WEB__WORKERS` | `2` | Worker processes (min 2) |
| `AUTHENTIK_WEB__THREADS` | `4` | Threads per worker |
| `AUTHENTIK_WEB__MAX_REQUESTS` | `1000` | Requests before worker restart (0=disable) |
| `AUTHENTIK_WEB__MAX_REQUESTS_JITTER` | `50` | Request limit jitter |
| `AUTHENTIK_WEB__PATH` | `/` | Service path prefix (needs leading+trailing `/`) |

## Worker (Dramatiq)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_WORKER__PROCESSES` | `1` | Worker processes |
| `AUTHENTIK_WORKER__THREADS` | `2` | Threads per worker (min 2) |
| `AUTHENTIK_WORKER__TASK_MAX_RETRIES` | `5` | Failed task retry attempts |
| `AUTHENTIK_WORKER__TASK_DEFAULT_TIME_LIMIT` | `minutes=10` | Task runtime limit |
| `AUTHENTIK_WORKER__TASK_PURGE_INTERVAL` | `days=1` | Old task cleanup interval |
| `AUTHENTIK_WORKER__TASK_EXPIRATION` | `days=30` | Task retention period |
| `AUTHENTIK_WORKER__SCHEDULER_INTERVAL` | `seconds=60` | Task scheduler frequency |
