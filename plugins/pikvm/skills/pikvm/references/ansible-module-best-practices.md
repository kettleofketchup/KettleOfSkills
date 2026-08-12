# Ansible Module Development Best Practices

## DOCUMENTATION String

```python
DOCUMENTATION = r'''
---
module: pikvm_msd
short_description: Manage PiKVM mass storage drive images
version_added: "1.0.0"
description:
    - Upload, remove, and manage ISO images on PiKVM MSD.
    - Connect/disconnect virtual drives with media type control.
    - Supports check mode and diff mode.
options:
    state:
        description:
            - Desired state of the MSD resource.
            - C(present) uploads image if missing. C(absent) removes image.
            - C(connected) mounts drive. C(disconnected) unmounts drive.
        type: str
        choices: [present, absent, connected, disconnected]
        default: present
    image:
        description: Image filename on PiKVM storage.
        type: str
        required: true
    src:
        description:
            - Local path to ISO file for upload.
            - Mutually exclusive with I(url).
        type: path
    url:
        description:
            - URL for PiKVM to download ISO from remotely.
            - Mutually exclusive with I(src).
        type: str
    cdrom:
        description: Mount as CD-ROM (true) or Flash drive (false).
        type: bool
        default: true
extends_documentation_fragment:
    - mynamespace.pikvm.pikvm_auth
requirements: ["python >= 3.9"]
author: ["Your Name (@githubhandle)"]
seealso:
    - module: mynamespace.pikvm.pikvm_info
'''
```

Markup: `L(text,url)` links, `U(url)` URLs, `M(module.name)` module refs, `I(option)` italics, `C(value)` code

## EXAMPLES String

```python
EXAMPLES = r'''
- name: Upload and mount Ubuntu ISO
  mynamespace.pikvm.pikvm_msd:
    pikvm_host: 10.0.0.100
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    state: present
    image: ubuntu-24.04.iso
    src: /isos/ubuntu-24.04-live-server-amd64.iso
    cdrom: true
    connected: true

- name: Remove an ISO image
  mynamespace.pikvm.pikvm_msd:
    pikvm_host: 10.0.0.100
    pikvm_user: admin
    pikvm_passwd: "{{ vault_pikvm_passwd }}"
    state: absent
    image: old-image.iso
'''
```

## RETURN String

```python
RETURN = r'''
image:
    description: Image filename on PiKVM.
    returned: always
    type: str
    sample: "ubuntu-24.04.iso"
msd_state:
    description: Current MSD state after operation.
    returned: success
    type: dict
    contains:
        connected:
            description: Whether drive is connected.
            type: bool
            returned: always
        cdrom:
            description: Whether drive is in CD-ROM mode.
            type: bool
            returned: always
msg:
    description: Human-readable status message.
    returned: always
    type: str
    sample: "Image uploaded and connected as CD-ROM"
'''
```

## argument_spec Keys

| Key | Description |
|-----|-------------|
| `type` | `str`, `int`, `float`, `bool`, `list`, `dict`, `path`, `raw`, `jsonarg`, `bytes`, `bits` |
| `required` | Only needed if `True` |
| `default` | Default value (None if unset) |
| `choices` | List of valid values |
| `aliases` | Alternative parameter names |
| `elements` | Element type for `type='list'` |
| `no_log` | `True` masks value in logs (secrets) |
| `options` | Nested argument_spec for `type='dict'` |
| `fallback` | `(env_fallback, ['ENV_VAR'])` tuple |

## AnsibleModule Constructor

```python
module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True,
    mutually_exclusive=[["src", "url"]],
    required_if=[
        ("state", "present", ("image",)),
        ("state", "absent", ("image",)),
    ],
    required_one_of=[["src", "url"]],
    required_together=[["cdrom", "image"]],
)
```

See [ansible-module-implementation.md](ansible-module-implementation.md) for doc fragments, check/diff mode, open_url client, and error handling patterns.
