# Grafana Foundation SDK (Python)

Grafana's official multi-language SDK for building dashboard JSON
programmatically. Source: <https://github.com/grafana/grafana-foundation-sdk>.

Use this **instead of hand-writing dashboard JSON** when:

- The dashboard has more than a handful of panels.
- You want the output to validate against Grafana Cloud's schema by
  construction (the SDK types are generated from the same CUE schemas
  Grafana itself ships).
- You want Grafana version compatibility automatic — picking
  `grafana-foundation-sdk@11.5.0` gives you a builder set that emits
  Grafana 11.5 dashboards.

## Install (Python)

PyPI release tags carry an **epoch prefix** (`1769699452!11.5.0` for
the 11.5.0 release). Poetry's caret constraint doesn't parse the
`!epoch` form cleanly, so pin the exact version:

```toml
# pyproject.toml — Poetry
[tool.poetry.group.dev.dependencies]
grafana-foundation-sdk = "1769699452!11.5.0"
```

For uv / PEP 621:

```toml
[dependency-groups]
dev = ["grafana-foundation-sdk==1769699452!11.5.0"]
```

Then `poetry lock && poetry install --with dev` (or `uv sync`).

Find current epoched version on PyPI: `curl -s https://pypi.org/pypi/grafana-foundation-sdk/json | jq '.releases | keys | last'`.

## Pick a model: V1 (classic) or V2 (Scenes)

Grafana 11 supports both. Which you pick determines the SDK module
namespace:

| Model | Module path | When to use |
|-------|-------------|-------------|
| V1 (classic) | `grafana_foundation_sdk.builders.dashboard.Dashboard` | Existing dashboards, ConfigMap provisioning, anywhere you currently hand-write `{"panels": [...]}` |
| V2 (Scenes) | `grafana_foundation_sdk.builders.dashboard_v2alpha1.Dashboard` | New dashboards in Grafana 11+ where you want the modern editor's full feature set (per-panel time ranges, library elements, conditional rendering). Required if the Grafana UI's Problems panel flags "Missing property 'layout'". |

V1 dashboards still load fine in Grafana 11+ (auto-migrated at render
time), so V1 is the lower-friction path for most additions.

## Build pattern (V1)

```python
from grafana_foundation_sdk.builders import dashboard, timeseries
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from grafana_foundation_sdk.models.common import (
    GraphDrawStyle, StackingMode, StackingConfig,
)

DS_LOKI = "${DS_LOKI}"

builder = (
    dashboard.Dashboard("DraftForge — Subsystem Logs")
    .uid("draftforge-subsystem-logs")
    .tags(["draftforge", "logs", "structlog"])
    .refresh("30s")
    .time("now-3h", "now")
    .with_row(dashboard.Row("Overview — all systems"))
    .with_panel(
        timeseries.Panel()
        .title("Log rate by system")
        .datasource({"type": "loki", "uid": DS_LOKI})
        .targets([
            {
                "expr": (
                    f'sum by (system) (rate('
                    f'{{service_name=~"$service", deployment_environment="$env"}} '
                    f'| json | __error__="" | system!="" [$__interval]))'
                ),
                "legendFormat": "{{system}}",
            }
        ])
        .stacking(StackingConfig(mode=StackingMode.NORMAL, group="A"))
        .draw_style(GraphDrawStyle.LINE)
        .span(12).height(8)
    )
)

import json
print(JSONEncoder(sort_keys=True, indent=2).encode(builder.build()))
```

## Build pattern (V2 / Scenes)

```python
from grafana_foundation_sdk.builders import (
    dashboard_v2alpha1 as dashboard, timeseries,
)
from grafana_foundation_sdk.models.dashboard_v2alpha1 import (
    GridLayoutItemKind, ElementReferenceKind,
)

builder = (
    dashboard.Dashboard("DraftForge — Subsystem Logs")
    .description("...")
    .tags(["draftforge", "logs"])
    .time_settings(
        dashboard.TimeSettings()
        .from_("now-3h").to("now").auto_refresh("30s")
    )
    .with_element(
        "panel-log-rate",
        timeseries.Panel().title("Log rate by system")
        # ...same target setup as V1
    )
    .layout(
        dashboard.GridLayout().with_item(
            GridLayoutItemKind(
                element=ElementReferenceKind(name="panel-log-rate"),
                x=0, y=0, width=12, height=8,
            )
        )
    )
)
```

The V2 model splits panels into the `elements` dict (keyed by name) and
the `layout.items` array (grid positions referring to those names) —
no more inline `gridPos`. This is the same model Grafana's V2 UI saves
to.

## Export to JSON for import

The SDK builder returns a typed model; serialize with `JSONEncoder`:

```python
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from pathlib import Path

Path("dashboard.json").write_text(
    JSONEncoder(sort_keys=True, indent=2).encode(builder.build()) + "\n"
)
```

The encoder emits JSON that matches the upstream schema exactly — no
hand-rolled fields, no missing defaults. Import via Grafana's
**Dashboards → New → Import → Upload JSON file** flow as usual.

## Reference impl

The project's structured-log dashboard at
`docs/dev/telemetry/dashboards/gen_dashboard.py` is the canonical
example. Mirror its structure for new code-driven dashboards:

1. Top of file: constants for datasource name, label-selector filter
   string, and `SAFE_JSON = "| json | __error__=\"\""` (defensive
   against jsonparsererr poisoning aggregates).
2. Helper funcs that wrap the SDK builders to apply project defaults
   (legend placement, stacking, unit `logs/s`, etc.).
3. A `SYSTEMS` list driving repeated per-system rows.
4. Self-validation at the end: assert the JSON parses, panel IDs are
   unique, datasource refs resolve. The SDK output passes Grafana
   schema validation by construction so structural checks are
   sanity-only.

## When NOT to use the SDK

- Quick one-off dashboard with 1–3 panels: hand-writing JSON or
  duplicating an existing one in the Grafana UI is faster than
  setting up Python imports.
- Provisioning via ConfigMap sidecar where you already have a
  reviewed/approved JSON: don't regenerate from SDK unless you're
  also rewriting the dashboard.
- Datasource or alerting resources: SDK covers dashboards only.

## Common gotchas

- **PyPI epoch versions.** Don't use `^11.0.0` — it won't match
  `1769699452!11.5.0`. Pin the exact `EPOCH!BASE` string.
- **Datasource references.** Pass `{"type": "...", "uid": "..."}` as
  a plain dict on `.datasource()` even though the SDK types accept a
  full `DataSourceRef`. The dict form survives JSON encoding cleanly.
- **`${DS_LOKI}` substitution.** Treat as a literal string in the
  `uid` field. Grafana's import dialog substitutes it via the
  `__inputs` block at the top of the JSON — see
  [dashboard-creation.md](dashboard-creation.md) for the inputs
  block.
- **V2 layout coordinates.** `width`/`height`/`x`/`y` on
  `GridLayoutItemKind`, not `w`/`h`/`x`/`y` like V1's `gridPos`.
