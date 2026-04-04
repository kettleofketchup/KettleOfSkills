# Cloudflare DNS Management Reference

*Last updated: 2026-03-23*

## Tunnel DNS Records

For Cloudflare Tunnel, hostnames need CNAME records pointing to the tunnel:

```bash
# Via cloudflared CLI
cloudflared tunnel route dns <tunnel-name> app.home.kettle.sh

# Creates: app.home.kettle.sh CNAME <tunnel-uuid>.cfargotunnel.com (proxied)
```

## API-Based DNS Management

### List DNS records

```bash
curl -s "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[] | {name, type, content, proxied}'
```

### Create CNAME for tunnel

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CNAME",
    "name": "app.home.kettle.sh",
    "content": "<tunnel-uuid>.cfargotunnel.com",
    "proxied": true
  }'
```

### Delete DNS record

```bash
curl -X DELETE "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}" \
  -H "Authorization: Bearer $CF_API_TOKEN"
```

## Opt-In Exposure Pattern

Only services with DNS records pointing to the tunnel are internet-accessible:

| Service | DNS Record | Exposed? |
|---------|-----------|----------|
| foundry.home.kettle.sh | CNAME → tunnel | Yes |
| grafana.home.kettle.sh | CNAME → tunnel | Yes |
| argocd.home.kettle.sh | No record | No (LAN only) |

**To expose a new service:**
1. Create CNAME record pointing to tunnel
2. Ensure IngressRoute exists with appropriate middleware
3. Optionally create Cloudflare Access application + policy

**To un-expose:**
1. Delete the CNAME record

## Local vs External DNS

When a hostname has a Cloudflare proxied CNAME:
- **External**: Resolves to Cloudflare IP → goes through tunnel
- **LAN**: Also resolves to Cloudflare IP unless local DNS overrides it

For split-horizon DNS (LAN goes direct to Traefik):
- Configure local DNS server (Pi-hole, router) with `*.home.kettle.sh → 192.168.5.200`
- External requests go through Cloudflare, local requests go direct

**IMPORTANT:** DNS-only (grey cloud) mode with a tunnel CNAME still resolves to Cloudflare IPs. To keep a hostname purely local, don't create any Cloudflare DNS record for it.

## Finding Zone ID and Account ID

```bash
# List zones
curl -s "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result[] | {name, id}'

# Account ID is in the zone details
curl -s "https://api.cloudflare.com/client/v4/zones/{zone_id}" \
  -H "Authorization: Bearer $CF_API_TOKEN" | jq '.result.account.id'
```

## just Recipes for DNS Management

```bash
just cf::list-dns                          # List all DNS records
just cf::expose <hostname>                 # Create CNAME → tunnel
just cf::unexpose <hostname>               # Delete CNAME
just cf::create-token <name>               # Create service token
just cf::add-app <hostname>                # Create Access application
just cf::allow-token <hostname> <token>    # Add service token policy
```
