---
description: Pattern matching, regex, numeric/array/logical matchers, gjson JSON path extraction
last_updated: 2026-03-18
---

# Goss Matchers

## Default Matching Behavior

- **Booleans, strings, integers**: Equality
- **Arrays**: Contains-elements (subset, not exact match)
- **io.Readers** (file contents, stdout, stderr, http body): Line-by-line pattern matching

## Pattern Syntax (io.Readers)

Used in `contents`, `stdout`, `stderr`, `body` fields:

| Pattern | Meaning |
|---------|---------|
| `"foo"` | Line contains substring "foo" |
| `"!foo"` | No line contains "foo" |
| `"/regex/"` | Line matches regex |
| `"!/regex/"` | No line matches regex |

```yaml
command:
  cat /etc/os-release:
    exit-status: 0
    stdout:
      - "Ubuntu"           # contains "Ubuntu"
      - "!Debian"           # does NOT contain "Debian"
      - "/^ID=ubuntu/"      # regex: line starts with ID=ubuntu
      - "!/error/i"         # no line matches "error" (case-insensitive NOT supported natively)
```

## Advanced Matchers

Use matcher objects for complex assertions. Wrap value in matcher key:

### String Matchers

```yaml
file:
  /etc/hostname:
    contents:
      - have-prefix: "web-"
      - have-suffix: ".local"
      - contain-substring: "prod"
      - match-regexp: "^web-[0-9]+"
      - equal: "web-01.local"      # exact match (entire content)
```

### Numeric Matchers

Auto-converts strings to numbers for comparison:

```yaml
command:
  nproc:
    exit-status: 0
    stdout:
      - gt: 1        # greater than
      - ge: 2        # greater or equal
      - lt: 128      # less than
      - le: 64       # less or equal
```

### Array Matchers

```yaml
user:
  deploy:
    groups:
      contain-element: "docker"          # has "docker" group
      contain-elements: [docker, sudo]   # has both
      consist-of: [docker, sudo, deploy] # exactly these (any order)
      equal: [deploy, docker, sudo]      # exactly these (exact order)
      have-len: 3                        # array length
```

### Logical Matchers

```yaml
command:
  cat /proc/meminfo:
    stdout:
      # AND - all must pass
      - and:
          - contain-substring: "MemTotal"
          - match-regexp: "[0-9]+ kB"
      # OR - any must pass
      - or:
          - contain-substring: "MemTotal"
          - contain-substring: "MemFree"
      # NOT - negation
      - not:
          contain-substring: "error"
```

### Semver Matcher

```yaml
command:
  nginx -v 2>&1:
    exit-status: 0
    stderr:
      - semver-constraint: ">=1.18.0"
```

### GJSON Matcher (JSON Path Extraction)

Extract fields from JSON output and apply matchers:

```yaml
command:
  curl -s http://localhost:8080/api/health:
    exit-status: 0
    stdout:
      - gjson:
          path: status
          content: "ok"
      - gjson:
          path: version
          content:
            semver-constraint: ">=2.0.0"
      - gjson:
          path: checks.#
          content:
            gt: 0
```

GJSON path syntax: `field.nested`, `array.#` (length), `array.0` (index), `array.#(name=="db").status` (filter).

### have-key Matcher

```yaml
# Verify object has specific key (useful with gjson)
matching:
  check_config:
    content:
      gjson:
        path: database
        content:
          have-key: "host"
```

## Gotchas

- Arrays default to subset matching; use `consist-of` or `equal` for exact matching
- Numeric matchers auto-convert; string "4" compared with `gt: 3` works
- Pattern matching on io.Readers is per-line; multiline patterns won't match
- `!pattern` negation means "no line in entire output matches"
- `equal` on io.Reader matches the entire content, not per-line
