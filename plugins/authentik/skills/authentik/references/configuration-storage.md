# Authentik Configuration: Storage, Outposts, Security

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
