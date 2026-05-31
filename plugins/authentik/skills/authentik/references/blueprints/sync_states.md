# Blueprint Sync States, Reapplication, and Cross-Blueprint References

How authentik blueprints actually behave on first apply, on reapply, and across separate blueprint files. The state field is the most operationally important knob — pick wrong and you'll either fight LDAP sync forever or ship a broken first-boot.

**Schema**: `https://goauthentik.io/blueprints/schema.json` — use as yaml-language-server header on every blueprint file for IDE validation of models, fields, tags, and state values.

## BlueprintInstance is keyed by file path, NOT metadata.name

Gotcha with real production impact: when authentik's discovery watcher picks up a file-backed blueprint, it creates a `BlueprintInstance` row keyed by the file's **path** (e.g. `mounted/cm-authentik-blueprints-ldap/ldap-source.yaml`). The instance's `name` field is populated from `metadata.name` **on first creation only** and is then stable in the DB.

Consequence: if a Helm chart conditionally toggles between two `metadata.name` values (e.g. `ldap-source-disabled` vs `graynet-ldap`) based on a values flag, the **first** name wins — authentik keeps that as the instance's identity forever, even when the file content flips to the other branch. The instance's `content` and `last_applied_hash` fields update, but the visible `name` in the admin UI stays stuck on whatever the file said at first boot.

**Fix for this pattern**: don't conditionally switch metadata.name between Helm if/else branches. Either (a) always emit the same `metadata.name` and gate the `entries:` list on the flag, or (b) emit two separate files with different paths so they create two distinct BlueprintInstance rows. Option (a) is cleaner — one file, one row, content changes based on the flag:

```yaml
version: 1
metadata:
  name: {{ .Values.ldap.slug }}   # stable name, NOT conditional
entries:
  {{- if .Values.ldap.enabled }}
  - model: authentik_sources_ldap.ldapsource
    ...
  {{- end }}
```

## state: values

| State | First apply | Subsequent applies | Use when |
|-------|------------|--------------------|----------|
| `present` (default) | create if missing | **update `attrs`** to reconcile drift | Object should always match the blueprint exactly |
| `created` | create if missing | **never touched** (even non-identifier attrs) | Seed a row that another system (LDAP sync, user) will own afterward |
| `must_created` | create if missing | **fail the entire blueprint** if exists | Strict ownership — refuse to reapply over hand-edits |
| `absent` | delete if exists | delete if exists | Decommissioning |

The asymmetry of `created` matters most: once the row exists, blueprint reapplies are no-ops on it. This is what you want when you're pre-creating placeholder rows that will be enriched by an external sync (LDAP, SCIM, OAuth source). Use `present` and you'll fight the sync on every reapply.

## Reapplication cadence

Blueprints reapply on a 60-minute timer by default (`AUTHENTIK_BLUEPRINTS_DISCOVERY_INTERVAL`). Each blueprint file is applied **atomically as a single DB transaction** — partial application is impossible. Either the whole file lands or none of it does. This means:

- A typo in entry 50 of 50 will roll back entries 1-49
- You can't mix `must_created` with reconcilable `present` entries safely — one failure aborts everything
- Cross-blueprint dependencies are async: file A's entries are NOT visible to file B during the same apply tick (they're separate transactions). For cross-file references, use `!Find` against the live DB, not in-flight blueprint state.

## Discovery sources

Blueprints come from three places:
1. **Local files** — `/blueprints/` inside server + worker pods, watched by inotify, auto-discovered
2. **OCI registries** — `oci://registry/path/blueprint:tag` references
3. **DB-stored** — `BlueprintInstance` rows created via API or Terraform provider

When a file disappears, authentik **does not** delete the objects it created — they persist. Use explicit `state: absent` entries for decommission, don't rely on file deletion.

## Cross-blueprint reference rules

`!KeyOf <id>` is **strictly intra-blueprint**. The id resolution iterates `blueprint.iter_entries()` on the currently-loading Blueprint object only — see `authentik/blueprints/v1/common.py` and upstream issue #10679 (the 2024.6.1 regression that confirmed this scoping). You **cannot** reference an `id:` from a different blueprint file. Two consequences:

1. If you need to reference an entry from another file, use `!Find [model, [field, value]]` which queries the live DB
2. If the referenced object doesn't exist yet at the time the second file is applied, `!Find` returns `null` and your blueprint silently degrades (e.g. an empty group binding). This is the source of the classic "first apply binds zero users to admin groups" problem.

## The first-boot chicken-and-egg pattern

Two blueprints, A and B:
- **A: blueprints-ldap** declares the LDAPSource and (importantly) pre-declares user rows with `state: created` at `path=goauthentik.io/sources/<slug>`
- **B: blueprints-users** binds those users to admin groups via `!Find [authentik_core.user, [username, X]]`

Without A's pre-creation step, on first boot B's `!Find` returns `null` because LDAP sync hasn't run yet (sync is on a 60-min schedule, separate from blueprint apply). Group bindings end up empty until the next sync + next blueprint apply tick.

With A's pre-creation, the user rows exist before B applies, `!Find` resolves immediately, and group bindings are populated on first boot. When LDAP sync eventually runs, it adopts the pre-created rows via `user_matching_mode: username_link` (see `ldap_sources.md`).

The user rows must use `state: created` (not `present`) so blueprint reapplies don't fight LDAP sync's attribute updates. The `name:` field in the pre-created entry is just a placeholder to satisfy User model validation — LDAP sync overwrites it with the AD displayName.

## When `!FindObject` is right instead of `!Find`

Added in 2025.8.0. Returns the full serialized model object instead of just the primary key. Use it when the consuming field expects a nested object (rare) instead of a foreign-key id. For binding properties to a user/group, `!Find` is still what you want.
