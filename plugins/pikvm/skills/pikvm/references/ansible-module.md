# PiKVM Ansible Module: Implementation Patterns

## Module Structure

```
plugins/
├── module_utils/
│   └── pikvm.py          # Shared PiKVM client (sync httpx wrapper)
└── modules/
    ├── pikvm_msd.py       # ISO upload, drive management
    ├── pikvm_atx.py       # Power control
    ├── pikvm_hid.py       # Keyboard/mouse input
    └── pikvm_info.py      # Device facts gathering
```

## Shared Arguments

All modules accept these common params:

```python
PIKVM_COMMON_ARGS = dict(
    pikvm_host=dict(type="str", required=True),
    pikvm_user=dict(type="str", required=True, no_log=False),
    pikvm_passwd=dict(type="str", required=True, no_log=True),
    pikvm_totp_secret=dict(type="str", required=False, no_log=True, default=None),
    pikvm_verify_ssl=dict(type="bool", default=False),
    pikvm_timeout=dict(type="float", default=30.0),
)
```

## pikvm_msd Module

```yaml
# Upload ISO and mount as CD-ROM
- pikvm_msd:
    pikvm_host: "{{ pikvm_ip }}"
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    state: present          # present/absent/connected/disconnected
    image: ubuntu-24.04.iso
    src: /path/to/ubuntu-24.04.iso  # local file (mutually exclusive with url)
    url: https://releases.ubuntu.com/24.04/ubuntu-24.04-live-server-amd64.iso
    cdrom: true             # true=CD-ROM, false=Flash
    rw: false               # read-write mode (ignored when cdrom=true)
    connected: true         # connect drive after upload
```

State logic:
- `present` — Upload image if not exists, set params. Idempotent (skip if image exists with same size)
- `absent` — Disconnect if connected, remove image
- `connected` — Connect drive with specified image/params
- `disconnected` — Disconnect drive

Return values: `changed`, `image`, `msd_state`, `msg`.

## pikvm_atx Module

```yaml
- pikvm_atx:
    pikvm_host: "{{ pikvm_ip }}"
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    state: "on"             # on/off/off_hard/reset_hard
    wait: true              # wait for completion
```

Idempotent: `state=on` does nothing if host already powered on (checks `leds.power`).

## pikvm_hid Module

```yaml
# Type text
- pikvm_hid:
    pikvm_host: "{{ pikvm_ip }}"
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    action: type            # type/shortcut/key
    text: "Hello World"     # for action=type
    keymap: en-us
    slow: false
    delay: 0.02

# Send shortcut
- pikvm_hid:
    pikvm_host: "{{ pikvm_ip }}"
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    action: shortcut
    keys: ["ControlLeft", "AltLeft", "Delete"]
```

## pikvm_info Module

```yaml
- pikvm_info:
    pikvm_host: "{{ pikvm_ip }}"
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    fields:                  # optional filter
      - hw
      - system
      - msd
      - atx
  register: pikvm_facts
```

Returns `pikvm_facts.info` (system info), `pikvm_facts.msd` (MSD state), `pikvm_facts.atx` (ATX state).

## Module Utils: Shared Client

```python
# plugins/module_utils/pikvm.py
import httpx

class PiKVMModuleClient:
    """Sync HTTP client for Ansible modules (no async in module context)."""

    def __init__(self, module):
        self.host = module.params["pikvm_host"]
        self.client = httpx.Client(
            base_url=f"https://{self.host}",
            verify=module.params["pikvm_verify_ssl"],
            timeout=module.params["pikvm_timeout"],
        )
        self._auth_headers = {
            "X-KVMD-User": module.params["pikvm_user"],
            "X-KVMD-Passwd": self._build_passwd(module),
        }

    def request(self, method, path, **kwargs):
        resp = self.client.request(method, path,
                                   headers=self._auth_headers, **kwargs)
        if resp.status_code in (401, 403):
            raise AuthError(resp.status_code)
        data = resp.json()
        if not data.get("ok"):
            raise APIError(data)
        return data.get("result", {})

    def get(self, path, **kw): return self.request("GET", path, **kw)
    def post(self, path, **kw): return self.request("POST", path, **kw)
```

## Idempotency Pattern

```python
def run_msd(module, client):
    current = client.get("/api/msd")
    desired_state = module.params["state"]

    if desired_state == "present":
        image = module.params["image"]
        existing = current["storage"]["images"].get(image)
        if existing and existing["complete"]:
            module.exit_json(changed=False, msg=f"{image} already present")
        # Upload needed
        ...
        module.exit_json(changed=True, msg=f"Uploaded {image}")
```

## Logging

Ansible modules use `module.log()` and `module.warn()`. Map PiKVM operations:
- `module.log(f"Uploading {image} to {host}")` at start
- `module.warn(f"MSD busy on {host}, waiting...")` on 409
- Return `msg` in exit_json for task output
