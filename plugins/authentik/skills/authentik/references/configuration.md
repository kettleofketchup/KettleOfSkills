# Authentik Configuration Reference

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

### Read Replicas

Indexed via `AUTHENTIK_POSTGRESQL__READ_REPLICAS__<index>__<setting>`.
Each replica accepts: `HOST`, `PORT`, `NAME`, `USER`, `PASSWORD`, `SSLMODE`, `SSLROOTCERT`, `SSLCERT`, `SSLKEY`, `CONN_MAX_AGE`, `CONN_HEALTH_CHECKS`, `DISABLE_SERVER_SIDE_CURSORS`, `CONN_OPTIONS`.

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
| `AUTHENTIK_LISTEN__HTTP` | `0.0.0.0:9000` | Server, Worker, Proxy outposts |
| `AUTHENTIK_LISTEN__HTTPS` | `0.0.0.0:9443` | Server, Proxy outposts |
| `AUTHENTIK_LISTEN__LDAP` | `0.0.0.0:3389` | LDAP outposts |
| `AUTHENTIK_LISTEN__LDAPS` | `0.0.0.0:6636` | LDAP outposts |
| `AUTHENTIK_LISTEN__METRICS` | `0.0.0.0:9300` | Prometheus metrics |
| `AUTHENTIK_LISTEN__DEBUG` | `0.0.0.0:9900` | Go debug |
| `AUTHENTIK_LISTEN__DEBUG_PY` | `0.0.0.0:9901` | Python debug |
| `AUTHENTIK_LISTEN__TRUSTED_PROXY_CIDRS` | RFC1918+loopback | Comma-separated CIDRs for proxy headers |

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

## Storage

Backend selection: `AUTHENTIK_STORAGE__BACKEND` = `file` (default) or `s3`.
Override per category: `AUTHENTIK_STORAGE__MEDIA__*` (icons), `AUTHENTIK_STORAGE__REPORTS__*` (CSV reports).

### File Backend

- `AUTHENTIK_STORAGE__FILE__PATH`: Storage directory (default: `/data`)
- `AUTHENTIK_STORAGE__FILE__URL_EXPIRY`: URL validity (default: `minutes=15`)

### S3 Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_STORAGE__S3__REGION` | - | S3 region |
| `AUTHENTIK_STORAGE__S3__ENDPOINT` | - | S3 endpoint URL |
| `AUTHENTIK_STORAGE__S3__USE_SSL` | `true` | HTTPS for S3 |
| `AUTHENTIK_STORAGE__S3__ACCESS_KEY` | - | Access key (hot-reloadable) |
| `AUTHENTIK_STORAGE__S3__SECRET_KEY` | - | Secret key (hot-reloadable) |
| `AUTHENTIK_STORAGE__S3__BUCKET_NAME` | - | Bucket name |
| `AUTHENTIK_STORAGE__S3__ADDRESSING_STYLE` | `auto` | `auto` or `path` |
| `AUTHENTIK_STORAGE__S3__CUSTOM_DOMAIN` | - | Custom URL domain |

## GeoIP & Events

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_EVENTS__CONTEXT_PROCESSORS__GEOIP` | `/geoip/GeoLite2-City.mmdb` | GeoIP City DB path (skipped if missing) |
| `AUTHENTIK_EVENTS__CONTEXT_PROCESSORS__ASN` | `/geoip/GeoLite2-ASN.mmdb` | GeoIP ASN DB path (skipped if missing) |

## Outposts

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_OUTPOSTS__CONTAINER_IMAGE_BASE` | `ghcr.io/goauthentik/%(type)s:%(version)s` | Image template. Placeholders: `%(type)s`, `%(version)s`, `%(build_hash)s` |
| `AUTHENTIK_OUTPOSTS__DISCOVER` | `true` | Auto-discover K8s/Docker integrations |

## Error Reporting

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_ERROR_REPORTING__ENABLED` | `false` | Send errors to Sentry |
| `AUTHENTIK_ERROR_REPORTING__SENTRY_DSN` | - | Sentry endpoint |
| `AUTHENTIK_ERROR_REPORTING__ENVIRONMENT` | `customer` | Environment tag |
| `AUTHENTIK_ERROR_REPORTING__SEND_PII` | `false` | Include personal data |

## Sessions & Security

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHENTIK_REPUTATION__EXPIRY` | `86400` | Reputation score retention (seconds) |
| `AUTHENTIK_SESSIONS__UNAUTHENTICATED_AGE` | `days=1` | Unauthenticated session lifetime (2025.4.0+) |
| `AUTHENTIK_LDAP__TASK_TIMEOUT_HOURS` | `2` | LDAP sync timeout |
| `AUTHENTIK_LDAP__PAGE_SIZE` | `50` | LDAP sync page size |

## Airgapped Deployment Settings

Disable all outbound connections for offline/airgapped environments:

```yaml
# Helm values.yaml
authentik:
  disable_update_check: true
  disable_startup_analytics: true
  error_reporting:
    enabled: false
```

| Variable | Value | Purpose |
|----------|-------|---------|
| `AUTHENTIK_DISABLE_UPDATE_CHECK` | `true` | Disable version check calls |
| `AUTHENTIK_DISABLE_STARTUP_ANALYTICS` | `true` | Disable startup analytics |
| `AUTHENTIK_ERROR_REPORTING__ENABLED` | `false` | Disable Sentry error reporting |
| `AUTHENTIK_OUTPOSTS__DISCOVER` | `false` | Disable auto-discovery (optional) |

Additional airgapped considerations:
- **Avatars**: Default uses Gravatar (outbound). Set to `initials` in System > Settings
- **GeoIP**: Provide DB files manually or accept disabled GeoIP (auto-skipped if missing)
- **Container images**: Mirror `ghcr.io/goauthentik/server` and outpost images to internal registry
- **Helm chart**: Mirror `https://charts.goauthentik.io` to internal chart repo
- **Outpost image base**: Set `AUTHENTIK_OUTPOSTS__CONTAINER_IMAGE_BASE` to internal registry

## Advanced

- **Custom Python settings**: Mount to `/data/user_settings.py` (unsupported, can break startup)
- **System settings**: Configurable via Admin UI > System > Settings or API
- **Deprecated**: `AUTHENTIK_POSTGRESQL__USE_PGBOUNCER` and `USE_PGPOOL` — use `DISABLE_SERVER_SIDE_CURSORS` instead
