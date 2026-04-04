# PiKVM API: ATX Power Management

## Get ATX State

| | |
|---|---|
| Method | `GET` |
| Route | `/api/atx` |

Response:
```json
{
  "ok": true,
  "result": {
    "enabled": true,
    "busy": false,
    "leds": {"power": true, "hdd": false}
  }
}
```

`busy=true` means ATX is performing an operation and won't accept new commands.
`leds.power` indicates host power state.

## Power Control

| | |
|---|---|
| Method | `POST` |
| Route | `/api/atx/power` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | no | `on` — turn on (no-op if already on). `off` — soft power off (short press). `off_hard` — long press (5+ sec). `reset_hard` — reset button press |
| `wait` | boolean | no | `1` = wait for completion, `0` = return immediately |

## Button Click

| | |
|---|---|
| Method | `POST` |
| Route | `/api/atx/click` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `button` | string | no | `power` — short click. `power_long` — long press (5+ sec). `reset` — reset click |
| `wait` | boolean | no | `1` = wait for completion, `0` = return immediately |

## Difference: power vs click

- `/api/atx/power?action=on` is **state-aware**: does nothing if host is already on
- `/api/atx/click?button=power` is **stateless**: always presses the button regardless

Use `power` for idempotent automation. Use `click` for raw button simulation.

## WebSocket Event

`atx_state` event with same structure as GET response: `enabled`, `busy`, `leds.power`, `leds.hdd`.
