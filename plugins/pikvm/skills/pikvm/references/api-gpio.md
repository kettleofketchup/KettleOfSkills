# PiKVM API: GPIO

## Get State

`GET /api/gpio` — Returns model (scheme with inputs/outputs, driver/pin config, pulse settings, view layout) and state (per-channel online/state/busy).

## Switch Channel

| | |
|---|---|
| Method | `POST` |
| Route | `/gpio/switch` |

**Note**: Route lacks `/api` prefix (upstream inconsistency).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | string | yes | Channel name (e.g. `__v3_usb_breaker__`) |
| `state` | boolean | yes | `1` = on, `0` = off |
| `wait` | boolean | no | `1` = return immediately, `0` = wait for completion |

## Pulse Channel

| | |
|---|---|
| Method | `POST` |
| Route | `/api/gpio/pulse` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | string | yes | Channel name |
| `delay` | float | no | Pulse duration in seconds (0 = default) |
| `wait` | boolean | no | `1` = return immediately, `0` = wait for completion |

## WebSocket Events

- `gpio_model_state` — Full model scheme on connect
- `gpio_state` — Per-channel state changes (inputs/outputs with online/state/busy)
