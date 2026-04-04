# LogQL Reference

## Stream Selectors

```logql
{namespace="argocd"}                          # exact match
{namespace!="kube-system"}                    # not equal
{namespace=~"rook-ceph|authentik"}            # regex match
{pod!~".*-join-.*"}                           # regex not match
{namespace="traefik", container="traefik"}    # AND (comma)
```

K8s labels via Alloy/Promtail: `namespace`, `pod`, `container`, `node_name`, `job`, `stream` (stdout/stderr)

## Filter Expressions

```logql
|=  "error"          # line contains (fastest)
!=  "health"         # line does NOT contain
|~  "5\\d{2}"        # regex match
!~  "timeout|cancel" # regex not match
```

Chain for AND logic: `{ns="x"} |= "error" != "timeout" != "context canceled"`

## Parsers

Place AFTER line filters for performance.

**JSON** (Traefik access logs, CNPG, Authentik):
```logql
| json                                    # all top-level keys
| json status="DownstreamStatus", method="RequestMethod"  # specific fields
| json server="request.server[0]"         # nested access
```

**Logfmt** (ArgoCD, many Go apps):
```logql
| logfmt                                  # all key=value pairs
| logfmt level, msg, app="application"    # specific keys
```

**Pattern** (positional extraction):
```logql
| pattern "<ip> - - <_> \"<method> <uri> <_>\" <status> <size>"
```

**Regexp** (named capture groups):
```logql
| regexp "(?P<level>\\w+)\\s+(?P<msg>.*)"
```

## Label Filters

After parsing, filter on extracted labels:
```logql
| json | status >= 500                    # numeric
| logfmt | level = "error"               # string
| json | duration > 500ms                # duration
| json | status >= 400 and method = "POST"  # boolean AND
| logfmt | level = "error" or level = "fatal"  # boolean OR
```

## Line Format

Rewrite log line content (Go template syntax):
```logql
| line_format "{{.level}} {{.msg}}"
| line_format "{{div .Duration 1000000}}ms {{.RequestMethod}} {{.RequestPath}}"
| line_format "{{if eq .level \"error\"}}ERROR: {{.msg}}{{else}}{{.msg}}{{end}}"
```

## Label Format

Rename or modify labels:
```logql
| label_format dst=src
| label_format severity="{{if eq .level \"error\"}}critical{{else}}{{.level}}{{end}}"
```

## Metric Queries

**Log range aggregations:**
```logql
rate({namespace="x"}[5m])               # entries/sec
count_over_time({namespace="x"}[5m])    # total entries
bytes_over_time({namespace="x"}[5m])    # bytes in window
bytes_rate({namespace="x"}[5m])         # bytes/sec
absent_over_time({namespace="x"}[5m])   # 1 if no logs
```

**Unwrap (extract numeric values from parsed labels):**
```logql
{ns="traefik"} | json | unwrap Duration | __error__=""
avg_over_time({...} | json | unwrap duration [5m])
quantile_over_time(0.99, {...} | json | unwrap Duration [5m]) by (RequestHost)
```

Functions: `sum_over_time`, `avg_over_time`, `max_over_time`, `min_over_time`, `first_over_time`, `last_over_time`, `stddev_over_time`, `quantile_over_time`, `rate`, `rate_counter`

**Aggregation operators:**
```logql
sum by (namespace) (rate({job=~".+"}[5m]))
topk(10, sum by (RequestHost) (rate({ns="traefik"} | json [5m])))
sort_desc(sum by (namespace) (count_over_time({job=~".+"}[5m])))
```

Supported: `sum`, `avg`, `count`, `min`, `max`, `topk`, `bottomk`, `sort`, `sort_desc`

**Useful modifiers:**
```logql
count_over_time({ns="x"}[1h] offset 24h)   # time offset
sum(...) or vector(0)                        # fallback for alerts
```

## Best Practices

1. Filter order: stream selector -> `|=`/`!=` -> `|~`/`!~` -> parser -> label filter (cheap first)
2. Apply `| json` only after line filters narrow results
3. Use `$__auto` interval in Grafana queries for auto-scaling
4. Add `| __error__=""` after unwrap to drop parse errors
5. Use `| drop __error__, __error_details__` to keep results clean
6. Prefer `|=` over `|~` -- string contains is faster than regex
7. Use `| decolorize` before parsers when logs contain ANSI colors
