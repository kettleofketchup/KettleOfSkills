# Forward-auth breaks XHR: the hourly token lapse

A production failure mode that looks like a network/timeout bug and is not. Read this
before debugging "the app randomly disconnects" or CORS errors behind authentik
forward-auth.

## Symptom

An SPA behind forward-auth works, then abruptly fails every API call. The console shows
one or both of:

```
Access to fetch at 'https://auth.example.com/application/o/authorize/?client_id=...'
(redirected from 'https://app.example.com/api/settings') from origin
'https://app.example.com' has been blocked by CORS policy: Response to preflight
request doesn't pass access control check: Redirect is not allowed for a preflight
request.

... has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is
present on the requested resource.
```

WebSocket/SSE apps surface it with no CORS text at all — just a bare `Disconnected
(check URL or network)`, because the handshake fails the same way. Reloading fixes it,
for about an hour.

## Root cause

`ProxyProvider.access_token_validity` defaults to **`hours=1`**. Expiry is **not**
silent: on the next request the outpost answers `302` to
`https://<authentikHost>/application/o/authorize/...` so the token can be re-minted.

- **Navigation:** invisible. The `user_login` stage's `session_duration` is `seconds=0`
  (until browser close), so the redirect round-trips and returns authenticated with no
  login prompt. Nobody notices. This is why the bug hides.
- **XHR / fetch / SSE / WebSocket:** fatal. The redirect crosses origin, so per the
  Fetch spec the browser applies CORS to the redirected request and bans redirects
  outright on anything preflighted. The page cannot intercept either error.

It is also **unrecoverable without a reload**: only a navigation can complete
`/outpost.goauthentik.io/callback`, so the token is never re-minted and the SPA
retry-storms against a redirect it can never follow. Blast radius scales with how
XHR-heavy an app is; an app doing its own SSO instead of forward-auth is immune.

## Diagnosis

Confirm before fixing. All three are cheap.

**1. Read the actual validity — never assume the default was overridden:**
```bash
kubectl -n authentik exec deploy/authentik-server -- ak shell -c "
from authentik.providers.proxy.models import ProxyProvider
from authentik.stages.user_login.models import UserLoginStage
for p in ProxyProvider.objects.all():
    print(p.name, p.access_token_validity, p.refresh_token_validity, p.mode)
for s in UserLoginStage.objects.all():
    print(s.name, s.session_duration, s.remember_me_offset)
"
```

**2. Find the 60-minute metronome.** Token re-mints appear as `/outpost.goauthentik.io/
callback` hits in the proxy access log. Consecutive entries ~60 min apart confirm it:
```
20:00:57 callback / 21:01:06 callback / 22:02:07 callback
```
A long gap after a burst of redirects is the wedge — it ends only at the manual reload.

**3. Prove the redirects are the failure, not a symptom.** In Traefik access logs (JSON,
via Loki), group by status and path for the affected host. A wedge shows a contiguous
block of `302` with **zero** `200` — a session-wide outage window, not path-specific:
```
| json | RequestHost="app.example.com"        # then tally DownstreamStatus by minute
```

Beware two false leads, both seen in a real investigation:
- **Aggregate ratios lie.** One endpoint showed 98% redirects vs 8% on another. That was
  the SPA's retry loop inflating the count, not path-specific behaviour. Bucket by time.
- **`DownstreamStatus: 0` is usually normal.** It means no status was ever written —
  i.e. a hijacked or long-polled connection. Check `Duration`: a tight cluster at one
  value (e.g. 125s across every sample, with `OriginDuration` matching) is the app's own
  long-poll window, not a proxy timeout.

## Fix — two halves, both required

### 1. Stop it firing hourly

```yaml
- model: authentik_providers_proxy.proxyprovider
  attrs:
    mode: forward_single
    external_host: https://app.example.com
    access_token_validity: days=7       # default hours=1 IS the bug
```

Two bounds on how long to go:

- **Ceiling:** must stay **under `refresh_token_validity`** (`days=30`). Past that
  there is no refresh token left to mint from and the user gets a full login instead.
- **Cost:** policy bindings are evaluated when the token is **minted**, not per
  request, so this value is also the **revocation lag** — remove someone from a group
  and they keep access until their current token expires. Make it a per-provider value
  with a global default, and shorten it on any provider whose group binding *is* the
  real access-control list.

The split below makes a lapse non-destructive, so length is a UX choice, not a
correctness one — set it by revocation tolerance, not by how annoying the lapse is.

### 2. Make the lapse fail cleanly

The outpost serves two forward-auth endpoints:

| Endpoint | Unauthenticated response | Use for |
|---|---|---|
| `/outpost.goauthentik.io/auth/traefik` | `302` to the authorize flow | document navigation |
| `/outpost.goauthentik.io/auth/nginx` | `401`, no `Location` | XHR / SSE / WebSocket |

`/auth/nginx` is named for nginx's `auth_request`, which needs a 401 to drive
`error_page 401`. **Nothing about it is nginx-specific** — Traefik consumes it fine and
no nginx need exist. Do not "correct" it back.

Define both middlewares, then select per request kind. Split on `Sec-Fetch-Mode`, **not**
on a path prefix: an app's XHR surface is rarely enumerable, and a missed path silently
reintroduces the wedge on exactly the endpoint nobody thought of.

```yaml
- match: Host(`app.example.com`) && HeaderRegexp(`Sec-Fetch-Mode`, `^(cors|same-origin|websocket)$`)
  priority: 20                       # explicit: default priority is rule LENGTH
  middlewares: [{name: authentik-forwardauth-api, namespace: authentik}]
- match: Host(`app.example.com`)
  priority: 10
  middlewares: [{name: authentik-forwardauth, namespace: authentik}]
```

`Sec-Fetch-Mode` is a forbidden header name, so page script cannot forge it — and there
is nothing to gain, since authorization is identical on both routes (same outpost, same
provider, same bindings). Only the failure mode differs. Omit `no-cors` so
`<script>`/`<img>` sub-resources keep the old behaviour; clients that send no
`Sec-Fetch-Mode` (curl, old browsers) fall through to the navigation route.

Send navigation to the **401** middleware and users get a bare 401 page instead of a
login prompt. Keep the two routes' `authResponseHeaders` lists in step.

## Notes

- A per-path exclusion such as `!PathPrefix(/v2/)` on a registry is this same bug,
  hand-patched for one non-browser client. Treat it as a symptom.
- Both halves matter: a longer token alone leaves an identical wedge, just rarer; the
  split alone yields a clean 401 an SPA still shows as "disconnected" unless it
  reloads on 401.
