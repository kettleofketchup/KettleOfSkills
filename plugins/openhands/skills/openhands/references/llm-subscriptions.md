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
