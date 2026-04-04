# PiKVM API: WebSocket

Real-time bidirectional communication for state monitoring and HID input.

## Connection

**Endpoint**: `wss://<pikvm-ip>/api/ws`

Authenticate via X-headers or cookie. Opening a session starts the video streamer; closing the last session stops it.

### Stream-free session

Append `?stream=0` to avoid starting streamer and not count toward client tracking:
```
wss://<pikvm-ip>/api/ws?stream=0
```

Use this for automation that only needs state monitoring.

## Initial Events on Connect

On connection, the server sends current state as individual events:

| Event Type | Content |
|------------|---------|
| `gpio_model_state` | GPIO model scheme (inputs/outputs, drivers, pins, pulse config, view) |
| `info_extras_state` | Extra services (VNC, IPMI: ports, daemon, enabled) |
| `info_hw_state` | Hardware platform + health (CPU/GPU temp, throttling, memory) |
| `info_meta_state` | Server hostname, KVM metadata |
| `info_system_state` | KVMD version, streamer app/version/features, kernel |
| `wol_state` | Wake-on-LAN config (enabled, IP, port, MAC) |
| `gpio_state` | All GPIO channel states (online, state, busy) |
| `hid_state` | HID status, keyboard LEDs, mouse online/mode |
| `atx_state` | ATX enabled, busy, power/hdd LEDs |
| `msd_state` | MSD enabled/online/busy, storage (images, free, uploading), drive state |
| `streamer_state` | Streamer limits, params, snapshot status, features |
| `loop` | Indicates event loop mode entered (no more initial state dumps) |

After `loop`, only change events are sent.

## Ping/Pong

Send: `{"event_type": "ping", "event": {}}`
Receive: `{"event_type": "pong", "event": {}}`

## Sending Key Events

```python
import websocket, ssl, json, time

ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
ws.connect("wss://<ip>/api/ws?stream=0",
           header={"X-KVMD-User": "admin", "X-KVMD-Passwd": "admin"})

# Key codes: https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/code/code_values
ws.send(json.dumps({"event_type": "key", "event": {"key": "Enter", "state": True}}))
time.sleep(0.05)
ws.send(json.dumps({"event_type": "key", "event": {"key": "Enter", "state": False}}))
ws.close()
```

## Event Format

All events follow: `{"event_type": "<type>", "event": {<data>}}`

Key event types for monitoring:
- `msd_state` — Track upload progress (`storage.uploading`), drive connection changes
- `atx_state` — Track power state changes (`leds.power`)
- `hid_state` — Track HID device availability
- `gpio_state` — Track GPIO channel changes
