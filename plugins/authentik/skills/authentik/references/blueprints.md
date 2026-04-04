# Authentik Blueprints

Declarative YAML config for flows, stages, providers, applications. Auto-discovered, reconciled every 60 min. Atomic transactions (all-or-nothing).

## Structure

```yaml
# yaml-language-server: $schema=https://goauthentik.io/blueprints/schema.json
version: 1
metadata:
  name: my-blueprint
  labels:
    blueprints.goauthentik.io/description: "What this does"
context:
  default_var: value
entries:
  - model: app_label.modelname
    state: present          # present|created|must_created|absent
    id: my-ref-id           # for !KeyOf references
    identifiers:
      slug: unique-id       # how to find existing object
    attrs:
      name: My Object       # fields to set
    conditions:
      - !Condition [AND, true]
```

## States

| State | Behavior |
|-------|----------|
| `present` | Create or update (default) |
| `created` | Create once, never update |
| `must_created` | Create or FAIL if exists |
| `absent` | Delete (cascading) |

## YAML Tags

| Tag | Usage | Description |
|-----|-------|-------------|
| `!KeyOf` | `!KeyOf my-id` | Resolve PK by entry `id` |
| `!Find` | `!Find [app.model, [field, value]]` | Query model instance PK |
| `!Env` | `!Env [VAR, default]` | Environment variable |
| `!File` | `!File [/path, default]` | Read file contents |
| `!Context` | `!Context [key, default]` | Runtime context variable |
| `!Format` | `!Format ["%s-fmt", !Context var]` | Python % string format |
| `!If` | `!If [cond, true_val, false_val]` | Conditional value |
| `!Condition` | `!Condition [AND, val1, val2]` | Boolean logic (AND/NAND/OR/NOR/XOR/XNOR) |
| `!Enumerate` | `!Enumerate [iterable, SEQ, template]` | Loop over items |
| `!Index` | `!Index 0` | Current iteration index |
| `!Value` | `!Value 0` | Current iteration value |

## Meta Models

- `authentik_blueprints.metaapplyblueprint` - Apply another blueprint as dependency
  ```yaml
  - model: authentik_blueprints.metaapplyblueprint
    identifiers:
      name: Default - Password change flow
    attrs:
      required: true
  ```

## Common Models

See [blueprints-models.md](blueprints-models.md) for the full model reference.

## Helm Chart: Native Blueprint ConfigMaps

The Helm chart has **built-in `blueprints.configMaps`** support. No manual volume mounts needed:

```yaml
# values.yaml
blueprints:
  configMaps:
    - authentik-blueprints-core     # ConfigMap names
    - authentik-blueprints-apps
  secrets: []                        # Can also mount from secrets
```

Only keys ending in `.yaml` are discovered. Create ConfigMaps alongside the Helm chart.

## Exporting Blueprints

Export existing config as starting point, then clean up:
```bash
# Full export (run inside worker container)
kubectl exec -n authentik deploy/authentik-worker -- ak export_blueprint

# Flow export: Admin UI → Flows → download icon next to flow
```

Exported blueprints use hardcoded PKs, no tags. Clean up by replacing PKs with `!Find`/`!KeyOf` references.

## Examples

See [blueprints-examples.md](blueprints-examples.md) for complete working examples:
- Authentication flow with stage bindings
- SAML provider + application + group policy
- OAuth2/OIDC provider (ArgoCD)
- Proxy provider (Traefik forward auth)
- Kubernetes ConfigMap with multiple blueprints
