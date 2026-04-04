# PiKVM API: Redfish (DMTF Standard)

Industry-standard [DMTF Redfish](https://www.dmtf.org/standards/redfish) implementation. Compatible with [Redfishtool](https://github.com/DMTF/Redfishtool).

## Endpoints

### Service Root (no auth required)

`GET /api/redfish/v1` → ServiceRoot.v1_6_0, RedfishVersion 1.6.0, Systems link.

### Systems Collection

`GET /api/redfish/v1/Systems` → ComputerSystemCollection with Members array.

### System Info

`GET /api/redfish/v1/Systems/0` → ComputerSystem.v1_10_0 with:
- `PowerState` — current power state
- `HostName` — hostname
- `Boot` — BootSourceOverrideEnabled, BootSourceOverrideTarget
- `Actions` — `#ComputerSystem.Reset` with allowed values, `#ComputerSystem.SetDefaultBootOrder`

### System Update (no-op)

`PATCH /api/redfish/v1/Systems/0` → Returns 204. Added for OKD/Kubernetes IPI compatibility.

### Power Control

`POST /api/redfish/v1/Systems/0/Actions/ComputerSystem.Reset`

JSON body:
```json
{"ResetType": "On"}
```

| ResetType | Description |
|-----------|-------------|
| `On` | Power on |
| `ForceOff` | Hard power off |
| `GracefulShutdown` | Graceful power off |
| `ForceRestart` | Hard reset |
| `ForceOn` | Force power on |
| `PushPowerButton` | Simulate power button press |

Returns 204 on success, 400 on invalid/missing ResetType.
