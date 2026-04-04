# PiKVM API: Authentication

All API endpoints require authentication. Three methods available, plus 2FA support.

## Methods

### X-Header Auth (preferred for automation)

Pass credentials per-request:
```
X-KVMD-User: admin
X-KVMD-Passwd: admin
```

### HTTP Basic Auth

Standard basic auth (no `WWW-Authenticate` header returned — for Prometheus/system compat only):
```
curl -k -u admin:admin https://<pikvm-ip>/api/info
```

### Session Cookie Auth

1. **Login**: `POST /api/auth/login`
   - Body: `user=admin&passwd=admin`
   - Optional: `expire=0` (session duration), `redirect=/kvm/` (KVMD >=4.108)
   - Returns: `Set-Cookie: auth_token=<hex_token>; Path=/`
   - Success: `200 OK`. Bad creds: `403 Forbidden`

2. **Check**: `GET /api/auth/check`
   - `200 OK` = authenticated
   - `401 Unauthorized` = no auth provided
   - `403 Forbidden` = invalid credentials/token

3. **Logout**: `POST /api/auth/logout`
   - Invalidates session token

### Redirect whitelist (KVMD >=4.152)

Configurable via `/etc/kvmd/override.yaml`:
```yaml
kvmd:
    auth:
        allow_redirects: ["/", "/kvm", "/kvm/"]
```

## 2FA (TOTP)

Append one-time code to password without spaces. Password `foobar` + code `123456` = `foobar123456`.

```python
import pyotp, time

secret = "3OBBOGSJRYRBZH35PGXURM4CMWTH3WSU"  # from /etc/kvmd/totp.secret
totp = pyotp.TOTP(secret)

# Handle borderline lifetime — retry or delay if <2s remaining
now = int(time.time())
remaining = totp.interval - (now % totp.interval)
if remaining < 2:
    time.sleep(remaining + 1)

password = base_password + totp.now()
```

## Endpoints

| Method | Route | Params | Description |
|--------|-------|--------|-------------|
| POST | `/api/auth/login` | `user`, `passwd`, `expire?`, `redirect?` | Create session |
| GET | `/api/auth/check` | — | Verify auth status |
| POST | `/api/auth/logout` | — | Invalidate session |
