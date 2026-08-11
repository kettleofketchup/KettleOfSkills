# External Auth (Git Provider Passthrough)

Lets workspaces clone and push without users pasting personal access tokens. Coder brokers the OAuth flow and
hands the token to the agent.

Distinct from `CODER_OIDC_*`, which authenticates users **to** Coder.

## Server Configuration

Indexed env vars, starting at `0`:

```dotenv
CODER_EXTERNAL_AUTH_0_ID="primary-github"
CODER_EXTERNAL_AUTH_0_TYPE=github
CODER_EXTERNAL_AUTH_0_CLIENT_ID=xxxxx
CODER_EXTERNAL_AUTH_0_CLIENT_SECRET=xxxxx
CODER_EXTERNAL_AUTH_0_REVOKE_URL=https://api.github.com/applications/<CLIENT_ID>/grant
```

Callback URL to register with the provider — the path segment must equal the `ID`:

```
https://coder.example.com/external-auth/primary-github/callback
```

| Variable | Purpose |
|----------|---------|
| `ID` | Identifier used in the callback URL and Terraform |
| `TYPE` | `github`, `gitlab`, `azure-devops`, `bitbucket-cloud`, `bitbucket-server`, `gitea` |
| `CLIENT_ID` / `CLIENT_SECRET` | OAuth app credentials |
| `AUTH_URL` / `TOKEN_URL` / `VALIDATE_URL` | Required for self-managed providers |
| `REGEX` | Route repo URLs to this provider by hostname pattern |
| `SCOPES` | Override default scopes |
| `DISPLAY_NAME` / `DISPLAY_ICON` | UI presentation |
| `NO_REFRESH` | Disable refresh-token use |
| `PKCE_METHODS` | `S256` or `none` |
| `REVOKE_URL` | Endpoint for revoking the grant |

## Self-Managed GitLab

```dotenv
CODER_EXTERNAL_AUTH_1_ID="primary-gitlab"
CODER_EXTERNAL_AUTH_1_TYPE=gitlab
CODER_EXTERNAL_AUTH_1_CLIENT_ID=xxxxx
CODER_EXTERNAL_AUTH_1_CLIENT_SECRET=xxxxx
CODER_EXTERNAL_AUTH_1_AUTH_URL="https://gitlab.example.com/oauth/authorize"
CODER_EXTERNAL_AUTH_1_TOKEN_URL="https://gitlab.example.com/oauth/token"
CODER_EXTERNAL_AUTH_1_VALIDATE_URL="https://gitlab.example.com/oauth/token/info"
CODER_EXTERNAL_AUTH_1_REGEX='gitlab\.example\.com'
```

`REGEX` is what makes multiple providers coexist — Coder picks the provider whose regex matches the repository
host being cloned.

## In Templates

```hcl
data "coder_external_auth" "github" {
  id = "primary-github"
}

resource "coder_agent" "main" {
  os   = "linux"
  arch = "amd64"
  env = {
    GITHUB_TOKEN = data.coder_external_auth.github.access_token
  }
}
```

Referencing the data source makes authentication **mandatory** — the workspace build blocks until the user
completes the OAuth flow in the dashboard. That's usually desirable for templates that clone on startup, but it
means an unauthenticated user sees a stalled build rather than an error.

Optional variant — let the workspace start and authenticate later:

```hcl
data "coder_external_auth" "github" {
  id       = "primary-github"
  optional = true
}
```

## In Workspaces

```bash
coder external-auth access-token primary-github
```

The Coder agent also installs a git credential helper, so `git clone` against a matching host generally works
with no extra setup.

Clone-on-start pattern:

```hcl
resource "coder_script" "clone" {
  agent_id     = coder_agent.main.id
  display_name = "Clone repo"
  run_on_start = true
  script       = <<-EOT
    #!/usr/bin/env bash
    set -euo pipefail
    [ -d ~/project/.git ] && exit 0
    git clone https://github.com/example/project.git ~/project
  EOT
}
```

## Passing the OIDC Token Instead

For internal services that accept the user's IdP token directly:

```hcl
env = {
  OIDC_ACCESS_TOKEN = data.coder_workspace_owner.me.oidc_access_token
}
```

Requires `offline_access` in `CODER_OIDC_SCOPES` for the token to remain valid past its initial lifetime.
Treat it as a credential — it carries the user's full IdP identity into a sandbox they control.
