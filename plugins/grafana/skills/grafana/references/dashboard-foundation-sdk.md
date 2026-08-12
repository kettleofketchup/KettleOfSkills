# Grafana Foundation SDK (Python)

Grafana's official multi-language SDK for building dashboard JSON programmatically.

Use this **instead of hand-writing dashboard JSON** when:
- The dashboard has more than a handful of panels.
- You want output validated against Grafana Cloud's schema by construction (types from same CUE schemas Grafana ships).
- You want Grafana version compatibility — `grafana-foundation-sdk@11.5.0` emits Grafana 11.5 dashboards.

## Install (Python)

PyPI release tags carry an **epoch prefix** (`1769699452!11.5.0` for the 11.5.0 release). Pin the exact version:

```toml
# pyproject.toml — Poetry
[tool.poetry.group.dev.dependencies]
grafana-foundation-sdk = "1769699452!11.5.0"

# uv / PEP 621
[dependency-groups]
dev = ["grafana-foundation-sdk==1769699452!11.5.0"]
```

Find current epoched version: `curl -s https://pypi.org/pypi/grafana-foundation-sdk/json | jq '.releases | keys | last'`.

## V1 vs V2 (Scenes) Model

| Model | Module path | When to use |
|-------|-------------|-------------|
| V1 (classic) | `grafana_foundation_sdk.builders.dashboard.Dashboard` | Existing dashboards, ConfigMap provisioning, hand-written JSON replacements |
| V2 (Scenes) | `grafana_foundation_sdk.builders.dashboard_v2alpha1.Dashboard` | New dashboards in Grafana 11+ with modern editor features (per-panel time ranges, conditional rendering). Required if the UI flags "Missing property 'layout'". |

V1 dashboards still load fine in Grafana 11+ (auto-migrated at render time).

## Build Pattern (V1)

```python
from grafana_foundation_sdk.builders import dashboard, timeseries
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from grafana_foundation_sdk.models.common import GraphDrawStyle, StackingMode, StackingConfig

DS_LOKI = "${DS_LOKI}"

builder = (
    dashboard.Dashboard("DraftForge — Subsystem Logs")
    .uid("draftforge-subsystem-logs")
    .tags(["draftforge", "logs"])
    .refresh("30s")
    .time("now-3h", "now")
    .with_row(dashboard.Row("Overview"))
    .with_panel(
        timeseries.Panel()
        .title("Log rate by system")
        .datasource({"type": "loki", "uid": DS_LOKI})
        .targets([{"expr": 'sum by (system) (rate({service_name=~"$service"} | json [$__interval]))',
                   "legendFormat": "{{system}}"}])
        .stacking(StackingConfig(mode=StackingMode.NORMAL, group="A"))
        .draw_style(GraphDrawStyle.LINE)
        .span(12).height(8)
    )
)

import json
print(JSONEncoder(sort_keys=True, indent=2).encode(builder.build()))
```

## Build Pattern (V2 / Scenes)

```python
from grafana_foundation_sdk.builders import dashboard_v2alpha1 as dashboard, timeseries
from grafana_foundation_sdk.models.dashboard_v2alpha1 import GridLayoutItemKind, ElementReferenceKind

builder = (
    dashboard.Dashboard("DraftForge — Subsystem Logs")
    .tags(["draftforge", "logs"])
    .time_settings(dashboard.TimeSettings().from_("now-3h").to("now").auto_refresh("30s"))
    .with_element("panel-log-rate", timeseries.Panel().title("Log rate by system"))
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

V2 splits panels into `elements` dict (keyed by name) and `layout.items` array — no inline `gridPos`.

## Export to JSON

```python
from grafana_foundation_sdk.cog.encoder import JSONEncoder
from pathlib import Path

Path("dashboard.json").write_text(
    JSONEncoder(sort_keys=True, indent=2).encode(builder.build()) + "\n"
)
```

For common gotchas, the reference impl pattern, and when NOT to use the SDK, see [dashboard-foundation-sdk-patterns.md](dashboard-foundation-sdk-patterns.md).
