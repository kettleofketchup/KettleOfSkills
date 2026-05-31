# Querying Loki logs with `logcli`

`logcli` is Grafana's dedicated Loki CLI — the best fit for log work specifically
(real `--since 7d`, `jsonl` output, `--tail`, batched exports). Prefer it over
generic API curling or the `gcx` CLI when pulling/parsing logs at the terminal.

## Install

```bash
go install github.com/grafana/loki/cmd/logcli@latest   # Go toolchain
# or grab a release binary:
#   https://github.com/grafana/loki/releases  (asset: logcli-<os>-<arch>.zip)
logcli --version
```

## Auth — point at the Grafana Cloud datasource proxy

Reuse the existing token (`~/.config/draftforge/grafana.env`: `GRAFANA_URL`,
`GRAFANA_TOKEN`). `logcli` appends `/loki/api/v1/...` to `LOKI_ADDR`, and the
Grafana datasource proxy exposes exactly that path — so set `LOKI_ADDR` to the
proxy and authenticate with the bearer token:

```bash
set -a; source ~/.config/draftforge/grafana.env; set +a
export LOKI_ADDR="$GRAFANA_URL/api/datasources/proxy/uid/grafanacloud-logs"
export LOKI_BEARER_TOKEN="$GRAFANA_TOKEN"
logcli labels service_name           # smoke test → backend, dtx-backend, discord
```

Auth env vars (flags override): `LOKI_ADDR`, `LOKI_BEARER_TOKEN`
(`LOKI_BEARER_TOKEN_FILE`), `LOKI_USERNAME`/`LOKI_PASSWORD` (basic-auth: user =
Grafana Cloud Loki instance ID, password = API token — only if hitting the raw
`logs-prod-*.grafana.net` endpoint instead of the proxy), `LOKI_ORG_ID`
(X-Scope-OrgID; not needed via the proxy).

## Share auth with gcx (sessions & bot tokens)

`gcx` logs in to **Grafana**, `logcli` hits **Loki** — independent tools, but a
Grafana **service-account / system-bot token** (`glsa_…`) authenticates both, so
the `GRAFANA_TOKEN` above can be one token shared across them:

```bash
TOKEN=glsa_xxx
gcx login mystack --server "$GRAFANA_URL" --token "$TOKEN" --yes   # gcx side
export LOKI_ADDR="$GRAFANA_URL/api/datasources/proxy/uid/grafanacloud-logs"
export LOKI_BEARER_TOKEN="$TOKEN"                                  # logcli side
```

Pull the token straight from a gcx context (confirm keys with `gcx config --help`):

```bash
export LOKI_BEARER_TOKEN="$(gcx config get contexts.<ctx>.grafana.token)"
export LOKI_ADDR="$(gcx config get contexts.<ctx>.grafana.server)/api/datasources/proxy/uid/grafanacloud-logs"
```

A browser/OAuth `gcx login` exposes no long-lived token — `logcli` can't ride
that session. For shared/automated use, mint a service-account (`glsa_…`) token.
(The raw `logs-prod-*` basic-auth password is a Cloud access-policy `glc_…` token.)

**logcli vs `gcx logs query`:** use `gcx logs query '{app="x"}' --from now-1h
--to now` when already logged in to Grafana (self-hosted needs the datasource
endpoint configured in gcx); use `logcli` for raw LogQL, `--tail`, and `jsonl`→`jq`.

## Subcommands

`query` (range), `instant-query`, `labels [name]`, `series '<selector>'`,
`stats '<selector>'`, `volume '<selector>'`.

## Key flags (vs the `gcx` quirks)

| flag | notes |
|------|-------|
| `--since=7d` | real Go-duration; supports `d`/`w` (unlike `gcx`'s `--since`) |
| `--from`/`--to` | RFC3339 (`--from="2026-05-30T00:00:00Z"`); for explicit windows |
| `--limit=N` | default 30 — raise it; `--batch=1000` controls server paging |
| `-o, --output` | `default`, `raw` (line bodies), `jsonl` (one JSON obj/line — pipe to `jq`) |
| `--forward` | oldest-first (default is newest-first) |
| `-t, --tail` | live follow |
| `-q, --quiet` | suppress query metadata on stderr |
| `--addr`/`--org-id`/`--bearer-token` | override the env vars |

## DraftForge recipes

```bash
# error breakdown for a structlog-JSON service (backend/celery)
logcli query '{service_name="backend"} | json | level="error"' --since=24h --limit=0 -o jsonl \
  | jq -r '.line | fromjson | .error_type // .event' | sort | uniq -c | sort -rn

# discord is MIXED (JSON interaction logs + plain-text discord.py lines):
# | json drops the plain text — use a line filter for those
logcli query '{service_name="discord"} |= "ERROR"' --since=24h --limit=0 -o raw

# follow one interaction across processes
logcli query '{service_name="backend"} | json | interaction_id="<id>"' --since=24h -o raw

# live tail prod errors
logcli query '{deployment_environment="prod"} | json | level="error"' --tail
```

Note: with `-o jsonl`, logcli wraps each entry as `{"labels":{…},"line":"…","timestamp":…}`
— the structlog JSON is the string in `.line`, so `fromjson` it before filtering.
Real service_name values: `backend`, `dtx-backend`, `discord`; env `deployment_environment="prod"`.
For LogQL syntax see [dashboards/logs-logql.md](dashboards/logs-logql.md).
