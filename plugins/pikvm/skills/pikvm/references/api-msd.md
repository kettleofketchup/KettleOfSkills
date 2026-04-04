# PiKVM API: Mass Storage Drive (MSD)

Primary subsystem for ISO upload and virtual storage device management.

## Get MSD State

| | |
|---|---|
| Method | `GET` |
| Route | `/api/msd` |

Response structure:
```json
{
  "ok": true,
  "result": {
    "enabled": true,
    "online": true,
    "busy": false,
    "storage": {
      "size": 50000000000,
      "free": 45000000000,
      "uploading": false,
      "downloading": false,
      "images": {
        "ubuntu.iso": {"complete": true, "size": 4000000000},
        "win11.iso": {"complete": true, "size": 5200000000}
      },
      "parts": {"sda1": {"size": 50000000000, "free": 45000000000, "writable": true}}
    },
    "drive": {
      "image": "ubuntu.iso",
      "connected": true,
      "cdrom": true,
      "rw": false
    },
    "features": {}
  }
}
```

## Upload ISO (Binary)

| | |
|---|---|
| Method | `POST` |
| Route | `/api/msd/write` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | string | yes | Target filename (e.g. `ubuntu.iso`) |

Body: raw binary ISO data. Use chunked transfer for progress tracking.

```bash
curl -X POST --data-binary @ubuntu.iso -k -u admin:admin \
  "https://<pikvm-ip>/api/msd/write?image=ubuntu.iso"
```

Monitor upload progress via WebSocket `msd_state` events — check `storage.uploading`.

## Upload ISO by URL (Remote Download)

| | |
|---|---|
| Method | `POST` |
| Route | `/api/msd/write_remote` |

**Long-polling request** — do not interrupt until complete.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | yes | HTTP(S) URL to download |
| `image` | string | no | Target filename (auto-derived from URL if omitted) |
| `timeout` | integer | no | Download timeout in seconds (default: 10) |

Preferred for large ISOs — offloads download to PiKVM device.

## Set Drive Parameters

| | |
|---|---|
| Method | `POST` |
| Route | `/api/msd/set_params` |

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `image` | string | no | Select active image | `filename.iso` |
| `cdrom` | boolean | no | Media type | `1` = CD-ROM, `0` = Flash |
| `rw` | boolean | no | Read-write mode (ignored when cdrom=1) | `1` = RW, `0` = RO |

## Connect/Disconnect Drive

| | |
|---|---|
| Method | `POST` |
| Route | `/api/msd/set_connected` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `connected` | boolean | yes | `1` = connect, `0` = disconnect |

**Must disconnect before changing image or params.**

## Remove Image

| | |
|---|---|
| Method | `POST` |
| Route | `/api/msd/remove` |

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | string | yes | Filename to delete |

**Must disconnect drive first if image is currently active.**

## Reset MSD

| | |
|---|---|
| Method | `POST` |
| Route | `/api/msd/reset` |

Drops all custom parameters, resets to default state. No parameters.

## Complete Workflow

```
1. GET  /api/msd                              # Check state
2. POST /api/msd/set_connected?connected=0    # Disconnect if connected
3. POST /api/msd/write?image=foo.iso          # Upload (binary body)
   — or —
   POST /api/msd/write_remote?url=https://...  # Remote download
4. POST /api/msd/set_params?image=foo.iso&cdrom=1  # Set CD-ROM mode
5. POST /api/msd/set_connected?connected=1    # Connect to host
6. GET  /api/msd                              # Verify state
```
