# Subscription-Based LLM Auth

Use a consumer plan (ChatGPT Plus/Pro) instead of metered API keys. OAuth replaces the API key; the SDK caches
credentials and refreshes tokens.

## Support Status

| Vendor | Status |
|--------|--------|
| OpenAI (ChatGPT Plus/Pro → Codex models) | Supported |
| Others | "More subscription providers will be added in future releases" |

Anthropic Claude Pro/Max subscription auth is **not** documented as supported in the OpenHands SDK as of this
writing. For Claude models, use an API key or route through LiteLLM. Re-check
`docs.openhands.dev/sdk/guides/llm-subscriptions` before assuming otherwise — this is the area most likely to
have changed.

## Two different OpenAI auth paths — do not confuse them

| Path | Used by | Credential store |
|------|---------|------------------|
| `LLM.subscription_login()` | OpenHands' **own** LLM calls | `~/.openhands/auth/openai_oauth.json` |
| ACP file credentials | the **codex** ACP harness (`agent_kind: acp`) | custom secret `CODEX_AUTH_JSON` |

They are independent. Signing in through one does nothing for the other, and both files can coexist on the
same instance — which makes "I'm logged in but codex says I'm not" a very easy state to reach. The rest of
this page is the first path; the second is below.

## ACP harness credentials (`CODEX_AUTH_JSON`)

`openhands/sdk/agent/acp_file_credentials.py`. An ACP agent declares `acp_file_secrets`, visible in every
conversation's `meta.json`:

```json
{"secret_name":"CODEX_AUTH_JSON","filename":"auth.json","env_var":"CODEX_HOME",
 "subdir":"codex","env_points_to":"dir"}
```

At session start the secret is written to `tempfile.mkdtemp(prefix="openhands-codex-")/auth.json`, `CODEX_HOME`
is pointed at that dir, and the dir is `rmtree`d on close.

**Dropping a file at `~/.codex/auth.json` therefore does nothing.** Only the secret is read. A persisted
`~/.codex` volume mount does *not* carry the login — it only accumulates codex's own state
(`state_*.sqlite`, `skills/`, `installation_id`) from unauthenticated fallback runs where `CODEX_HOME` is
unset. Login persistence rides on `~/.openhands`, which holds the encrypted secret.

`GOOGLE_APPLICATION_CREDENTIALS_JSON` works the same way for gemini-cli (`env_points_to: "file"`).

### The validator is offline and structural

`is_valid_codex_auth()` runs **before codex ever starts** and only checks shape:

1. parses as JSON
2. `auth_mode` ∈ (absent, `"chatgpt"`)
3. `tokens.refresh_token` is a non-empty string

An **api-key-style auth.json is rejected outright** — it has no `tokens` object. Subscription OAuth only.

| Error surfaced in the UI | What it actually means |
|---|---|
| `ACPAuthRequired` / "ChatGPT authentication is invalid. Please sign in again." | The JSON failed the shape check. **Not** expiry, **not** a blocked network. |
| `ACPAuthRequired` / `[-32000] Authentication required` | No secret set at all; `CODEX_HOME` unset, codex fell back to `~/.codex`. |

### Paste it as one line

The most common cause of the first error is a terminal-wrapped paste: copying a pretty-printed `auth.json`
out of a wrapped terminal injects literal newlines *inside* the JWT string values, and `json.loads` fails on
the control characters. The tokens themselves are fine.

```bash
jq -c . ~/.codex/auth.json | wl-copy -n      # or xclip / pbcopy
```

Pipe straight to the clipboard — never `cat` it and mouse-select.

### Diagnosing on a live pod

Decrypt the stored secret with OpenHands' own cipher and run its own validator, printing structure only:

```python
# use /usr/local/bin/python3 — a /opt/venv python on PATH may not have openhands.sdk
from openhands.sdk.utils.cipher import Cipher                    # Fernet, key = OH_SECRET_KEY
from openhands.sdk.agent.acp_file_credentials import is_valid_codex_auth
# OH_SECRET_KEY is readable from /proc/<agent-server-pid>/environ
pt = Cipher(key).try_decrypt_str(secrets["custom_secrets"]["CODEX_AUTH_JSON"]["secret"])
print(is_valid_codex_auth(pt))
```

Confirm end-to-end without starting a paid session by materializing to a throwaway `CODEX_HOME` and running
`codex login status` → `Logged in using ChatGPT`.

### Rotation is automatic

When codex refreshes the token mid-session, the lifecycle's monitor thread writes the new `auth.json` back
into the secret, so `last_refresh` advances on its own. No periodic re-paste is needed — if you see a stored
value that differs from what you pasted, that is the write-back working, not corruption.

## Usage

```python
from openhands.sdk import LLM

llm = LLM.subscription_login(
    vendor="openai",
    model="gpt-5.2-codex",
)
```

First call opens a browser for OAuth with OpenAI. Credentials cache to `~/.openhands/auth/` and refresh
automatically on later runs.

### Options

| Option | Effect |
|--------|--------|
| `force_login=True` | Discard cache, re-authenticate |
| `open_browser=False` | Print the auth URL instead of launching a browser — required on headless servers |
| `llm.is_subscription` | Property confirming subscription mode is active |

```python
llm = LLM.subscription_login(vendor="openai", model="gpt-5.2-codex", open_browser=False)
assert llm.is_subscription
```

## Model Strings

| Model | Notes |
|-------|-------|
| `gpt-5.2-codex` | Default, latest |
| `gpt-5.2` | Base model |
| `gpt-5.1-codex-max` | High-capacity |
| `gpt-5.1-codex-mini` | Lightweight |

## Headless / Container Setup

The OAuth flow needs a browser once. On a server:

1. Run with `open_browser=False`, copy the printed URL, complete it in a local browser.
2. Or authenticate on a workstation and copy `~/.openhands/auth/` to the server.

In Docker, persist `~/.openhands` (already required for settings) so the cache survives restarts:

```bash
-v ~/.openhands:/.openhands
```

Without that volume, every container restart forces a fresh OAuth flow — which nothing can complete
unattended.

## Constraints

Consumer subscriptions carry usage limits designed for interactive use, and their terms differ from API
plans. Agent loops consume tokens far faster than chat. Before standardizing a team on this:

- Confirm the subscription terms permit programmatic/agent use.
- Expect rate limiting under sustained agent workloads.
- Credentials are per-person and browser-bound — they don't fit shared multi-user servers, where a gateway
  with per-user virtual keys is the correct model.

The cached token in `~/.openhands/auth/` is a live credential for that person's account. On a shared host,
anyone who can read the volume can use their subscription.

## When to Use

| Scenario | Recommendation |
|----------|----------------|
| Individual developer, own machine | Subscription login — predictable cost |
| Individual, occasional heavy use | API key with `MAX_BUDGET_PER_TASK` |
| Team / shared deployment | LiteLLM gateway with per-user virtual keys (→ `llm-config.md`) |
| CI / automation | API key or gateway — no interactive OAuth available |
