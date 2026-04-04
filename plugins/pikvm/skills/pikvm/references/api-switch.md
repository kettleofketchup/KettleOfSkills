# PiKVM API: Switch

Multi-port KVM switching for daisy-chained PiKVM Switch devices. Port numbering: 0-19 continuous or float format (integer = unit number, fractional = port on unit). Up to 20 ports.

## Get State

`GET /api/switch` — Returns current switch state with all port info.

## Port Selection

**Previous**: `POST /api/switch/set_active_prev` — No params
**Next**: `POST /api/switch/set_active_next` — No params
**Specific**: `POST /api/switch/set_active`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `port` | float | yes | Port number: integer 0-19 or float (e.g. 2.1) |

## Beacon

`POST /api/switch/set_beacon`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `state` | boolean | yes | `1` = on, `0` = off |
| `port` | float | no | Port beacon (0-19 or float) |
| `uplink` | integer | no | Uplink beacon number |
| `downlink` | integer | no | Downlink beacon number |

## Port Parameters

`POST /api/switch/set_port_params`

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `port` | float | yes | Port number | `0..19` |
| `edid_id` | string | no | EDID UUID | UUID string |
| `dummy` | boolean | no | Pretend display attached | `1`/`0` |
| `name` | string | no | Port name | ASCII alphanumeric |
| `atx_click_power_delay` | float | no | Power click delay | `0..10` |
| `atx_click_power_long_delay` | float | no | Long power delay | `0..10` |
| `atx_click_reset_delay` | float | no | Reset click delay | `0..10` |

## Beacon Color

`POST /api/switch/set_colors`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `beacon` | hex | yes | Format: `RRGGBB:brightness:blink_ms` (e.g. `FFA500:BF:0028`) |

## Reboot Device

`POST /api/switch/reset`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `unit` | integer | yes | Unit number `0..4` |
| `bootloader` | boolean | no | Enter reflash mode after reboot |

## EDID Management

**Create**: `POST /api/switch/edids/create` — `name` (string, required), `data` (hex EDID binary, required)
**Change**: `POST /api/switch/edids/change` — `id` (UUID, required), `name` (optional), `data` (optional)
**Remove**: `POST /api/switch/edids/remove` — `id` (UUID, required)

## Per-Port ATX

**Power**: `POST /api/switch/atx/power` — `port` (float, required), `action` (required: `on`/`off`/`off_hard`/`reset_hard`)
**Click**: `POST /api/switch/atx/click` — `port` (float, required), `button` (required: `power`/`power_long`/`reset`)
