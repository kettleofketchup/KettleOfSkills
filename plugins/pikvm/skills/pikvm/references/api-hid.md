# PiKVM API: HID (Human Interface Device)

Keyboard and mouse input emulation.

## Get HID State

| | |
|---|---|
| Method | `GET` |
| Route | `/api/hid` |

Response includes: busy, connected, enabled, jiggler (active/enabled/interval), keyboard (leds: caps/num/scroll, online, outputs: active/available), mouse (absolute, online, outputs: active/available).

## Set Parameters

| | |
|---|---|
| Method | `POST` |
| Route | `/api/hid/set_params` |

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `keyboard_output` | string | no | Keyboard emulation type | `usb`, `ps2`, `disabled` |
| `mouse_output` | string | no | Mouse emulation type | `usb`, `usb_win98`, `usb_rel`, `ps2`, `disabled` |
| `jiggler` | boolean | no | Mouse jiggler toggle | `true`/`false` |

## Set Connected State

| | |
|---|---|
| Method | `POST` |
| Route | `/api/hid/set_connected` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `connected` | boolean | yes | `1` = connect, `0` = disconnect |

## Reset

`POST /api/hid/reset` — Resets HID to initial state. No params.

## Get Keyboard Layouts

`GET /api/hid/keymaps` — Returns available keymaps and default. Keymaps include: ar, bepo, cz, da, de, de-ch, en-gb, en-us, en-us-altgr-intl, en-us-colemak, es, et, fi, fo, fr, fr-be, fr-ca, fr-ch, hr, hu, is, it, ja, lt, lv, mk, nl, no, pl, pt, pt-br, ru, sl, sv, th, tr.

## Type Text

| | |
|---|---|
| Method | `POST` |
| Route | `/api/hid/print` |

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `limit` | integer | no | Max chars (0=unlimited, default 1024) | `>=0` |
| `keymap` | string | no | Keyboard layout | Any from `/api/hid/keymaps` |
| `slow` | boolean | no | Slow typing mode | `true`/`false` |
| `delay` | float | no | Inter-keystroke delay (seconds) | `0..5.0` (default 0.02 when slow) |

Body: raw text string. Example: `curl -X POST -d "Hello World" -k -u admin:admin https://<ip>/api/hid/print`

## Send Shortcut

| | |
|---|---|
| Method | `POST` |
| Route | `/api/hid/events/send_shortcut` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `keys` | string | yes | Comma-separated key names from [keymap.csv](https://github.com/pikvm/kvmd/blob/master/keymap.csv) |

Example: `?keys=ControlLeft,AltLeft,Delete`

## Send Key Event

| | |
|---|---|
| Method | `POST` |
| Route | `/api/hid/events/send_key` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | yes | Key from keymap.csv |
| `state` | boolean | no | `true` = press, `false` = release |
| `finish` | boolean | no | Auto-release non-modifier keys (default false) |

## Mouse Events

**Button**: `POST /api/hid/events/send_mouse_button`
- `button` (required): `left`, `middle`, `right`, `up`, `down`
- `state` (optional): `true` = press, `false` = release

**Absolute move**: `POST /api/hid/events/send_mouse_move`
- `to_x`, `to_y` (required): integer coordinates (0,0 = screen center)

**Relative move**: `POST /api/hid/events/send_mouse_relative`
- `delta_x`, `delta_y` (required): pixel offset

**Scroll**: `POST /api/hid/events/send_mouse_wheel`
- `delta_x`, `delta_y` (required): scroll amount
