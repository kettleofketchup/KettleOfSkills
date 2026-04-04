# PiKVM API: System

## Get System Info

| | |
|---|---|
| Method | `GET` |
| Route | `/api/info` |

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `fields` | string | no | Filter categories | `auth`, `extras`, `fan`, `hw`, `meta`, `system` |

Response fields by category:
- **hw**: platform (type, base, board, model, serial, video), health (cpu_percent, memory, temp, throttling flags)
- **system**: kvmd version, streamer app/version/features, kernel info
- **meta**: server hostname, KVM metadata
- **extras**: VNC/IPMI service info (ports, daemon, enabled)
- **fan**: fan status
- **auth**: auth config

Each category maps to a WebSocket event: `info_hw_state`, `info_system_state`, etc.

Example: `GET /api/info?fields=hw,system`

## Get System Log

| | |
|---|---|
| Method | `GET` |
| Route | `/api/log` |

| Param | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `follow` | boolean | no | Long-polling real-time log | `1`/`true`/`yes` or `0`/`false`/`no` |
| `seek` | integer | no | Log window in seconds | `>=0` |

Returns **plain text** (not JSON). Example: `GET /api/log?follow=1&seek=3600`

## Prometheus Metrics

| | |
|---|---|
| Method | `GET` |
| Route | `/api/export/prometheus/metrics` |

Returns Prometheus exposition format (plain text). Use with HTTP Basic Auth for scrape config.
