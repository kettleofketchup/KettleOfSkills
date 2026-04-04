# PiKVM API: Streamer

## Get State

`GET /api/streamer` — Returns features (h264, quality, resolution), limits, params, snapshot status, streamer details (encoder, h264 stats, sinks, source fps/resolution, stream clients).

## Take Snapshot

| | |
|---|---|
| Method | `GET` |
| Route | `/api/streamer/snapshot` |

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `save` | boolean | no | Save snapshot | `1`/`0` |
| `load` | boolean | no | Load existing snapshot | `1`/`0` |
| `allow_offline` | boolean | no | Allow when offline | `1`/`0` |
| `ocr` | boolean | no | Perform OCR text recognition | `1`/`0` |
| `ocr_langs` | string | no | OCR languages | 3-letter codes: `eng`, `deu`, etc. |
| `ocr_left` | integer | no | OCR region X (default -1) | `>=0` |
| `ocr_top` | integer | no | OCR region Y (default -1) | `>=0` |
| `ocr_right` | integer | no | OCR region width (default -1) | `>=0` |
| `ocr_bottom` | integer | no | OCR region height (default -1) | `>=0` |
| `preview` | boolean | no | Generate preview | `1`/`0` |
| `preview_max_width` | integer | no | Preview max width | `>0` |
| `preview_max_height` | integer | no | Preview max height | `>0` |
| `preview_quality` | integer | no | Preview JPEG quality (default 80) | `0..100` |

**Response Content-Type**:
- `ocr=true` → `text/plain` (recognized text)
- Default/`preview=true` → `image/jpeg` (binary image)
- Unavailable → `503`

OCR coordinate origin: top-left corner of captured frame.

## Delete Snapshot

`DELETE /api/streamer/snapshot` — Remove saved snapshot. No params.

## Get OCR State

`GET /api/streamer/ocr` — Returns enabled (bool), langs (available list, default list).

## WebSocket Event

`streamer_state` — Limits, params, snapshot saved status, features.
