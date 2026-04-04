---
description: Go text/template with Sprig functions, variables, conditionals, loops, conditional skip
last_updated: 2026-03-18
---

# Goss Templating

Goss uses Go `text/template` with Sprig function library (~100+ functions).

## Variables

Pass via `--vars <file>` (YAML/JSON) or `--vars-inline '<json>'`:

```bash
goss validate --vars vars.yaml
goss validate --vars-inline '{"env": "prod", "port": 8080}'
# --vars-inline overrides --vars when both provided
```

**vars.yaml example:**
```yaml
env: production
expected_owner: www-data
ports:
  - 80
  - 443
packages:
  - nginx
  - curl
```

Access in gossfile: `{{.Vars.env}}`, `{{.Vars.expected_owner}}`

## Template Variables

| Variable | Source |
|----------|--------|
| `{{.Vars.key}}` | From --vars file or --vars-inline |
| `{{.Env.HOME}}` | Environment variables (uppercase) |

## Conditionals

```yaml
{{if eq .Vars.env "production"}}
service:
  nginx:
    enabled: true
    running: true
{{end}}

{{if ne .Env.CI "true"}}
port:
  tcp:22:
    listening: true
{{end}}
```

## Loops

```yaml
package:
{{range .Vars.packages}}
  {{.}}:
    installed: true
{{end}}

port:
{{range .Vars.ports}}
  tcp:{{.}}:
    listening: true
{{end}}
```

## Sprig Functions (Common)

### String

| Function | Example |
|----------|---------|
| `lower` | `{{.Vars.name \| lower}}` |
| `upper` | `{{.Vars.name \| upper}}` |
| `trim` | `{{.Vars.name \| trim}}` |
| `replace` | `{{"foo" \| replace "o" "0"}}` |
| `contains` | `{{if contains "prod" .Vars.env}}` |
| `hasPrefix` | `{{if hasPrefix "web" .Vars.host}}` |
| `hasSuffix` | `{{if hasSuffix ".com" .Vars.domain}}` |
| `default` | `{{.Vars.owner \| default "root"}}` |
| `quote` | `{{.Vars.name \| quote}}` |
| `join` | `{{.Vars.list \| join ","}}` |
| `split` | `{{$parts := split "." .Vars.host}}` |

### Math

`add`, `sub`, `mul`, `div`, `mod`, `max`, `min`

### Type Conversion

`toString`, `toInt`, `toFloat64`, `toBool`, `toJson`, `fromJson`

### List/Dict

`list`, `first`, `last`, `append`, `has`, `dict`, `get`, `set`, `keys`, `values`

## Conditional Skip

Use `skip` with templates to conditionally disable tests:

```yaml
service:
  firewalld:
    enabled: true
    running: true
    skip: '{{if eq .Vars.env "dev"}}true{{end}}'

file:
  /etc/ssl/private/cert.pem:
    exists: true
    skip: '{{if ne .Vars.env "production"}}true{{end}}'
```

## Debugging Templates

```bash
goss render                    # Show rendered gossfile
goss render --debug            # Debug template rendering
goss render --vars vars.yaml   # Render with variables
```

Render output is a valid gossfile with all templates expanded and includes merged. Pipe to `goss validate -g -` for single-pass validation.

## Gotchas

- Template expressions must produce valid YAML after rendering
- Use `default` function to handle missing variables gracefully
- Escape dots in variable names using index: `{{index .Vars "my.dotted.key"}}`
- `--vars-inline` overrides values from `--vars` file
- Template errors surface at render time, not validation time
- Whitespace control: `{{-` trims leading, `-}}` trims trailing whitespace
