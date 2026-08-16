# Upstream

Vendored from [blader/humanizer](https://github.com/blader/humanizer), MIT, v2.9.1.

`SKILL.md` and `LICENSE` are upstream verbatim. `config.yaml` is ours — the marketplace
generator reads it to place the plugin under a category, and upstream has no such file.

## Refreshing

    git clone --depth 1 https://github.com/blader/humanizer /tmp/humanizer
    cp /tmp/humanizer/SKILL.md /tmp/humanizer/LICENSE plugins/humanizer/skills/humanizer/
    just sync-marketplace

Upstream ships the skill as a whole plugin repo (`.claude-plugin/`, `agents/`, `.github/`,
`scripts/validate-package.py`). Only `SKILL.md` carries the rules, so the rest is deliberately
not vendored — check the upstream release notes before assuming a new version still holds to that.
