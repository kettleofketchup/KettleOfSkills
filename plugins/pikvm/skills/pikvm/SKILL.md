---
name: pikvm
description: PiKVM HTTP API Python library and Ansible module/collection development. Use when building Python clients for PiKVM KVM-over-IP devices, creating Ansible modules/collections for PiKVM automation (ansible-creator, ansible-dev-tools, ansible-test, ansible-lint), scaffolding Ansible collections with galaxy.yml, writing module argument_spec/DOCUMENTATION/EXAMPLES/RETURN strings, implementing check_mode/diff_mode, creating doc_fragments, using module_utils with open_url, uploading ISOs via MSD API, managing virtual storage devices, controlling ATX power, sending HID input, taking screenshots with OCR, or interacting with any PiKVM REST endpoint.
---

# PiKVM HTTP API

Python library and Ansible module for PiKVM KVM-over-IP device automation.

## API Overview

Base URL: `https://<pikvm-ip>`. All responses return `{"ok": true/false, "result": {...}}` unless noted. Self-signed TLS certificates are default.

### Subsystems

| Subsystem | Reference | Key Endpoints |
|-----------|-----------|---------------|
| Authentication | [api-auth.md](references/api-auth.md) | Login, session tokens, 2FA/TOTP, X-header auth |
| System | [api-system.md](references/api-system.md) | Device info, logs, Prometheus metrics |
| MSD (Mass Storage) | [api-msd.md](references/api-msd.md) | ISO upload, virtual drive connect/disconnect, media type |
| ATX Power | [api-atx.md](references/api-atx.md) | Power on/off, reset, button clicks |
| HID Input | [api-hid.md](references/api-hid.md) | Keyboard/mouse events, text typing, shortcuts |
| GPIO | [api-gpio.md](references/api-gpio.md) | Switch/pulse GPIO channels |
| Streamer | [api-streamer.md](references/api-streamer.md) | Video state, snapshots, OCR |
| Switch | [api-switch.md](references/api-switch.md) | Multi-port KVM switching, EDID, per-port ATX |
| Redfish | [api-redfish.md](references/api-redfish.md) | DMTF standard power control |
| WebSocket | [api-websocket.md](references/api-websocket.md) | Real-time state events, key/mouse input |

## Python Library Architecture

See [python-library.md](references/python-library.md) for implementation patterns.

Core design:
- `PiKVMClient` class wrapping `httpx.AsyncClient` (async) with sync convenience wrappers
- Session-based auth with automatic token management and 2FA/TOTP support
- Subsystem methods: `client.msd.upload()`, `client.atx.power()`, `client.hid.type_text()`
- Progress callbacks for ISO uploads via chunked streaming
- Structured logging via `logging` module with operation context

## Ansible Collection & Module Development

### Collection Setup

See [ansible-collection-setup.md](references/ansible-collection-setup.md) for:
- `ansible-creator` scaffolding (`ansible-creator init collection`, `add plugin module`)
- Collection directory structure (galaxy.yml, meta/runtime.yml, plugins/, tests/)
- Testing with `ansible-test` (sanity, unit, integration)
- `ansible-lint` configuration and profile levels
- CI/CD with GitHub Actions

### Module Best Practices

See [ansible-module-best-practices.md](references/ansible-module-best-practices.md) for:
- DOCUMENTATION, EXAMPLES, RETURN string format and fields
- `argument_spec` keys and `AnsibleModule` constructor params
- Check mode and diff mode implementation
- Doc fragments for shared auth options (`extends_documentation_fragment`)
- Module utils: `open_url` from `ansible.module_utils.urls` (NOT httpx/requests)
- Error handling with `fail_json` and optional dependency patterns

### PiKVM-Specific Module Patterns

See [ansible-module.md](references/ansible-module.md) for PiKVM module implementations.

Core modules:
- `pikvm_msd` — Upload ISO, set media type (cdrom/flash), connect/disconnect drive
- `pikvm_atx` — Power on/off/reset with state detection
- `pikvm_hid` — Type text, send shortcuts, configure HID params
- `pikvm_info` — Gather device facts (system, hardware, health)

**Key distinction:** The standalone Python library uses `httpx` for async support. Ansible module_utils MUST use `open_url` from `ansible.module_utils.urls` for portability (no external dependencies).

## ISO Upload and Virtual Storage Workflow

The primary workflow for ISO management:

1. **Check MSD state** — `GET /api/msd` to verify enabled, online, not busy
2. **Upload ISO** — `POST /api/msd/write?image=name.iso` with binary body (or `POST /api/msd/write_remote` for URL-based download)
3. **Set media params** — `POST /api/msd/set_params?image=name.iso&cdrom=1`
4. **Connect drive** — `POST /api/msd/set_connected?connected=1`
5. **Monitor state** — Poll `GET /api/msd` or subscribe via WebSocket for `msd_state` events

Track upload progress via WebSocket `msd_state` events (storage.uploading field). For large ISOs, use `write_remote` with URL to offload download to PiKVM.

## Error Handling

All API errors follow: `{"ok": false, "result": {"error": "ErrorType", "error_msg": "details"}}`.
Common errors: `401 Unauthorized` (no auth), `403 Forbidden` (bad credentials), `409 Conflict` (device busy), `503 Unavailable`.

## Logging Best Practices

- Log every API call at DEBUG level with method, endpoint, params
- Log state transitions (MSD connect/disconnect, ATX power changes) at INFO
- Log upload progress (percentage, bytes transferred) at INFO with throttling
- Log errors with full response body at ERROR level
- Include PiKVM hostname in log context for multi-device environments
