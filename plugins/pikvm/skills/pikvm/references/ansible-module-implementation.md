# Ansible Module Implementation Patterns

## Doc Fragments

`plugins/doc_fragments/pikvm_auth.py`:
```python
class ModuleDocFragment:
    DOCUMENTATION = r'''
options:
    pikvm_host:
        description: PiKVM device hostname or IP.
        type: str
        required: true
    pikvm_user:
        description: PiKVM username.
        type: str
        required: true
    pikvm_passwd:
        description: PiKVM password. Appended with TOTP code if I(pikvm_totp_secret) set.
        type: str
        required: true
        no_log: true
    pikvm_totp_secret:
        description: TOTP secret for 2FA (base32 encoded).
        type: str
        no_log: true
    pikvm_verify_ssl:
        description: Validate SSL certificates.
        type: bool
        default: false
    pikvm_timeout:
        description: API request timeout in seconds.
        type: float
        default: 30.0
'''
```

Usage: `extends_documentation_fragment: mynamespace.pikvm.pikvm_auth`

## Check Mode

```python
module = AnsibleModule(argument_spec=args, supports_check_mode=True)

current = client.get("/api/msd")
if needs_change(current, desired):
    result["changed"] = True
    if module.check_mode:
        module.exit_json(**result)
    # Apply actual changes only if not check mode
    client.post("/api/msd/write", ...)
module.exit_json(**result)
```

## Diff Mode

```python
import json

if module._diff:
    result["diff"] = dict(
        before=json.dumps(current_state, indent=2, sort_keys=True) + "\n",
        after=json.dumps(desired_state, indent=2, sort_keys=True) + "\n",
        before_header=f"pikvm://{host}/msd/{image}",
        after_header=f"pikvm://{host}/msd/{image}",
    )
```

## Module Utils: open_url vs Third-Party

**Ansible modules MUST use `ansible.module_utils.urls`** — never `requests` or `httpx`:

```python
# plugins/module_utils/pikvm_client.py
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
import json

class PiKVMClient:
    def __init__(self, host, user, passwd, totp_secret=None, verify_ssl=False, timeout=30):
        self.base_url = f"https://{host}"
        self.verify = verify_ssl
        self.timeout = timeout
        self.headers = {
            "X-KVMD-User": user,
            "X-KVMD-Passwd": self._build_passwd(passwd, totp_secret),
            "Content-Type": "application/json",
        }

    def _request(self, method, path, data=None):
        url = f"{self.base_url}{path}"
        body = json.dumps(data) if data else None
        try:
            resp = open_url(url, headers=self.headers, method=method,
                           data=body, validate_certs=self.verify, timeout=self.timeout)
            content = resp.read()
            result = json.loads(content) if content else {}
        except HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            if e.code in (401, 403):
                raise AuthError(f"Authentication failed: {e.code}")
            raise APIError(f"{method} {path} returned {e.code}: {body_text}")
        except URLError as e:
            raise ConnectionError(f"Cannot reach {url}: {e}")
        if not result.get("ok"):
            raise APIError(result.get("result", {}).get("error_msg", "Unknown error"))
        return result.get("result", {})
```

The standalone Python library (`pikvm` package) can use `httpx` for async support. The Ansible module_utils wrapper MUST use `open_url` for portability.

## Info/Facts Module Pattern

Info modules MUST: set `supports_check_mode=True`, never make changes, always return `changed=False`.

```python
def main():
    module = AnsibleModule(argument_spec=args, supports_check_mode=True)
    client = PiKVMClient.from_module(module)
    info = client.get("/api/info")
    msd = client.get("/api/msd")
    module.exit_json(changed=False, info=info, msd=msd)
```

## Error Handling

```python
try:
    result = client.post("/api/msd/write", ...)
except AuthError as e:
    module.fail_json(msg=f"PiKVM auth failed: {e}", **result)
except APIError as e:
    module.fail_json(msg=f"PiKVM API error: {e}", **result)
except ConnectionError as e:
    module.fail_json(msg=f"Cannot reach PiKVM: {e}", **result)
```

Import third-party packages in try/except for clean error messages:
```python
try:
    import pyotp
    HAS_PYOTP = True
except ImportError:
    HAS_PYOTP = False

def main():
    if module.params.get("pikvm_totp_secret") and not HAS_PYOTP:
        module.fail_json(msg="pyotp required for 2FA: pip install pyotp")
```
