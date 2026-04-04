# Nextcloud Apps Configuration

## Installing Apps

```bash
NEXTCLOUD_POD=$(kubectl get pod -n nextcloud -l app.kubernetes.io/name=nextcloud -o jsonpath='{.items[0].metadata.name}')
OCC="kubectl exec -n nextcloud $NEXTCLOUD_POD -- su -s /bin/sh www-data -c"

# List installed apps
$OCC "php occ app:list"

# Install and enable
$OCC "php occ app:install <app_name>"
$OCC "php occ app:enable <app_name>"
```

Or via Helm lifecycle hooks (runs on install/upgrade):

```yaml
nextcloud:
  hooks:
    post-installation: |-
      php occ app:install calendar
      php occ app:install contacts
      php occ app:install talk
      php occ app:install richdocuments
      php occ app:install user_saml
```

## Calendar

- **App**: `calendar` (bundled, just enable)
- CalDAV endpoint: `https://cloud.example.com/remote.php/dav/calendars/<user>/`
- Supports CalDAV sync with Thunderbird, iOS, Android (DAVx5)
- No additional configuration needed after install

## Contacts

- **App**: `contacts` (bundled, just enable)
- CardDAV endpoint: `https://cloud.example.com/remote.php/dav/addressbooks/users/<user>/`
- Supports CardDAV sync with same clients as Calendar

## Nextcloud Talk

- **App**: `spreed` (Talk)
- Provides: chat, video calls, screen sharing
- For TURN/STUN (required for NAT traversal in video calls):

```bash
$OCC "php occ talk:turn:add turn:coturn.example.com:3478 udp --secret=<shared_secret>"
$OCC "php occ talk:stun:add stun:coturn.example.com:3478"
```

- High Performance Backend (HPB) is optional, improves signaling for 4+ participants
- Without HPB, internal signaling works for small groups

## Collabora CODE (Office Suite)

**Free, open source (MPL-2.0), self-hosted. No hard connection limit.**

If deployed via Helm subchart (`collabora.enabled: true`), install the Nextcloud connector:

```bash
$OCC "php occ app:install richdocuments"
$OCC "php occ app:enable richdocuments"
```

Configure in Nextcloud admin (Administration > Nextcloud Office):
- Select "Use your own server"
- URL: `https://collabora.example.com`
- Allow list: leave empty or add Nextcloud FQDN

### Collabora Helm Values (subchart)

Key settings in `collabora:` section of Nextcloud values:

```yaml
collabora:
  enabled: true
  collabora:
    aliasgroups:
      - host: "https://cloud.example.com"  # MUST match Nextcloud external URL
    extra_params: "--o:ssl.enable=false"    # Traefik handles TLS
    server_name: collabora.example.com
```

### Collabora Gotchas

- `aliasgroups.host` must exactly match Nextcloud external URL or WOPI fails
- Disable internal SSL when reverse proxy handles TLS (`--o:ssl.enable=false`)
- Collabora needs its own subdomain/IngressRoute (port 9980)
- Resource-hungry: allocate 500m-4000m CPU, 1-4Gi memory
- No HPA support (breaks collaborative editing)

## Recommended App Stack

| App | Package | Purpose |
|-----|---------|---------|
| `calendar` | Bundled | CalDAV calendar |
| `contacts` | Bundled | CardDAV contacts |
| `spreed` | Bundled | Talk (chat/video) |
| `richdocuments` | App Store | Collabora connector |
| `user_saml` | App Store | Authentik SSO |
| `deck` | Bundled | Kanban boards |
| `notes` | App Store | Markdown notes |
| `tasks` | App Store | CalDAV tasks |
| `groupfolders` | App Store | Shared folders with ACL |
