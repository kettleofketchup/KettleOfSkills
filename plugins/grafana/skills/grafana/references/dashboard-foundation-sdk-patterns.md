# Grafana Foundation SDK — Patterns and Gotchas

## Reference Implementation

The canonical example is `docs/dev/telemetry/dashboards/gen_dashboard.py`. Mirror its structure for new code-driven dashboards:

1. **Top of file**: constants for datasource name, label-selector filter string, and `SAFE_JSON = "| json | __error__=\"\""` (defensive against jsonparsererr poisoning aggregates).
2. **Helper funcs**: wrap SDK builders to apply project defaults (legend placement, stacking, unit `logs/s`, etc.).
3. **`SYSTEMS` list**: drives repeated per-system rows.
4. **Self-validation**: assert JSON parses, panel IDs are unique, datasource refs resolve. SDK output passes Grafana schema validation by construction so structural checks are sanity-only.

## Common Gotchas

**PyPI epoch versions.** Don't use `^11.0.0` — it won't match `1769699452!11.5.0`. Pin the exact `EPOCH!BASE` string.

**Datasource references.** Pass `{"type": "...", "uid": "..."}` as a plain dict on `.datasource()` even though the SDK types accept a full `DataSourceRef`. The dict form survives JSON encoding cleanly.

**`${DS_LOKI}` substitution.** Treat as a literal string in the `uid` field. Grafana's import dialog substitutes it via the `__inputs` block at the top of the JSON. See [dashboard-creation.md](dashboard-creation.md) for the inputs block.

**V2 layout coordinates.** `width`/`height`/`x`/`y` on `GridLayoutItemKind`, not `w`/`h`/`x`/`y` like V1's `gridPos`.

## When NOT to Use the SDK

- Quick one-off dashboard with 1–3 panels: hand-writing JSON or duplicating an existing one in the Grafana UI is faster.
- Provisioning via ConfigMap sidecar where you already have a reviewed/approved JSON: don't regenerate from SDK unless rewriting the dashboard.
- Datasource or alerting resources: SDK covers dashboards only.

## `__inputs` Block for Import

For dashboards with variable datasource UIDs, add an `__inputs` block so Grafana's import dialog prompts for the datasource:

```json
{
  "__inputs": [
    {
      "name": "DS_LOKI",
      "label": "Loki",
      "description": "",
      "type": "datasource",
      "pluginId": "loki",
      "pluginName": "Loki"
    }
  ],
  "title": "...",
  "panels": [...]
}
```

The SDK doesn't emit this block automatically — add it to the JSON after `JSONEncoder` serialization if you distribute the dashboard for import.

## Validating SDK Output

```python
import json
from grafana_foundation_sdk.cog.encoder import JSONEncoder

data = builder.build()
raw = JSONEncoder(sort_keys=True, indent=2).encode(data)

# Parse back to verify
parsed = json.loads(raw)
assert parsed["uid"] == "expected-uid"
panel_ids = [p["id"] for p in parsed.get("panels", []) if "id" in p]
assert len(panel_ids) == len(set(panel_ids)), "Duplicate panel IDs"
```
