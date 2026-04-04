# Logging Configuration

Control what Open WebUI logs, where it goes, and how it's formatted.

Open WebUI has two logging surfaces: the browser console for frontend debugging and the Python backend for server-side events.

## Frontend Logging

The frontend uses standard browser `console.log()` calls. Open your browser's developer tools (F12 or Cmd+Option+I on macOS), navigate to the Console tab.

## Backend Logging

The backend uses Python's built-in `logging` module. By default, logs are written to stdout at the INFO level.

### Log Levels

| Level | Value | When to use |
|---|---|---|
| `CRITICAL` | 50 | Catastrophic failures; the application may terminate |
| `ERROR` | 40 | Failed operations; the application continues but something broke |
| `WARNING` | 30 | Unexpected situations: deprecations, resource pressure |
| `INFO` | 20 | Normal operation flow: startup, key events, request handling (default) |
| `DEBUG` | 10 | Detailed diagnostic output: function calls, variable values, execution steps |

### Setting the Global Log Level

Set `GLOBAL_LOG_LEVEL` to change verbosity for the entire backend. This configures the root Python logger via `logging.basicConfig(force=True)`.

**Docker:**

```bash
--env GLOBAL_LOG_LEVEL="DEBUG"
```

**Docker Compose:**

```yaml
environment:
  - GLOBAL_LOG_LEVEL=DEBUG
```

Use `DEBUG` for development and troubleshooting. For production, stick with `INFO` or `WARNING`.

### Structured JSON Logging

For production environments using log aggregators, set `LOG_FORMAT=json` to switch all stdout output to single-line JSON objects.

**Docker:**

```bash
--env LOG_FORMAT="json"
```

**Docker Compose:**

```yaml
environment:
  - LOG_FORMAT=json
```

**JSON fields:**

| Field | Description |
|---|---|
| `ts` | ISO 8601 timestamp |
| `level` | Log level (`debug`, `info`, `warn`, `error`, `fatal`) |
| `msg` | Log message |
| `caller` | Source location (`module:function:line`) |
| `extra` | Additional context data (if any) |
| `error` | Error details (if applicable) |
| `stacktrace` | Stack trace (if applicable) |

**Example output:**

```json
{"ts": "2026-02-22T20:14:53.386+00:00", "level": "info", "msg": "GLOBAL_LOG_LEVEL: INFO", "caller": "open_webui.env"}
{"ts": "2026-02-22T20:15:02.245+00:00", "level": "info", "msg": "Context impl SQLiteImpl.", "caller": "alembic.runtime.migration"}
```

Notes:
- Default behavior (no `LOG_FORMAT` set) is unchanged: plain-text output
- The ASCII banner is suppressed when `LOG_FORMAT=json`
- JSON logging covers both early startup logs (stdlib `logging`) and runtime logs (Loguru)
