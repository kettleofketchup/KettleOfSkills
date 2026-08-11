# Coder Networking

## Access URLs

| Variable | Meaning |
|----------|---------|
| `CODER_ACCESS_URL` | The URL agents, CLI, and browsers use. Must be reachable **from inside workspace networks**, not just from laptops. |
| `CODER_WILDCARD_ACCESS_URL` | `*.coder.example.com` — enables `subdomain = true` on `coder_app` |

A common self-host mistake: setting `CODER_ACCESS_URL` to a public hostname that workspace pods can't resolve
because split-horizon DNS points elsewhere. Agents then build fine and never register. Test from a workspace:

```bash
kubectl run -n coder-workspaces test --rm -it --image=curlimages/curl -- \
  curl -sv https://coder.example.com/api/v2/buildinfo
```

## Subdomain Apps

`subdomain = true` serves each app at `<slug>--<agent>--<workspace>--<user>.coder.example.com`. This requires:

1. Wildcard DNS `*.coder.example.com` → the ingress
2. A certificate covering both apex and wildcard (cert-manager **DNS-01**; HTTP-01 cannot issue wildcards)
3. `CODER_WILDCARD_ACCESS_URL` set

Path-based apps (`subdomain = false`) avoid all of that but share an origin, so cookies and service workers
from different apps collide. Prefer subdomain apps for anything stateful; use path apps when you can't get a
wildcard certificate.

## Connection Path

Agents establish an outbound connection; users connect via WireGuard-based tunnels (Tailscale-derived).
Direct peer-to-peer is attempted first, falling back to a DERP relay run by `coderd`.

```
CODER_DERP_SERVER_ENABLE=true                 # built-in relay (default)
CODER_DERP_SERVER_STUN_ADDRESSES=disable      # air-gapped: no public STUN
CODER_BLOCK_DIRECT=true                       # Premium: force relay, no P2P
```

In air-gapped clusters set `CODER_DERP_SERVER_STUN_ADDRESSES=disable`, otherwise every connection attempt
stalls on unreachable public STUN servers before falling back.

Diagnose from a client:

```bash
coder ping <workspace>          # shows p2p vs DERP and latency
coder speedtest <workspace>
coder netcheck
```

## Workspace Proxies (Premium)

Regional relays that terminate app/terminal traffic near the user while `coderd` stays central.

```bash
coder wsproxy create --name=newyork --display-name="US East" --icon="/emojis/1f1fa-1f1f8.png"
# token is shown once
```

`values-wsproxy.yaml`:

```yaml
coder:
  workspaceProxy: true
  env:
    - name: CODER_PRIMARY_ACCESS_URL
      value: "https://coder.example.com"
    - name: CODER_PROXY_SESSION_TOKEN
      valueFrom: { secretKeyRef: { name: coder-proxy-token, key: token } }
    - name: CODER_ACCESS_URL
      value: "https://east.coder.example.com"
    - name: CODER_WILDCARD_ACCESS_URL
      value: "*.east.coder.example.com"
  tls:
    secretNames: [east-coder-tls]
```

```bash
helm install coder-east coder-v2/coder -n coder-east -f values-wsproxy.yaml
coder wsproxy ls
```

Each proxy needs its own hostname, its own wildcard, its own certificate, and its own token. Proxies relay app
and terminal traffic only — the dashboard and API always hit the primary.

## TLS

Two options:

**Terminate at the ingress** (typical): `coderd` speaks HTTP internally; ensure the ingress forwards
`X-Forwarded-Proto` so redirects don't downgrade.

**Terminate at coderd**:

```yaml
coder:
  tls:
    secretNames: [coder-tls]
  env:
    - name: CODER_TLS_ENABLE
      value: "true"
```

For a private CA, mount the bundle and set `SSL_CERT_FILE`. trust-manager can sync the bundle into the `coder`
and workspace namespaces so agents also trust it.

## Ports & Sharing

Users forward ports with `coder port-forward` or the dashboard. Sharing level is governed per app by
`coder_app.share` (`owner`/`authenticated`/`public`) and capped deployment-wide:

```
CODER_MAX_PORT_SHARE_LEVEL=authenticated     # forbid public sharing
```

Set this if workspaces run on infrastructure where an accidentally public port would be reachable from the
internet.
