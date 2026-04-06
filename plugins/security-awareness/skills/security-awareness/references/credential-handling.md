# Credential and Sensitive Data Handling

## Read Before Sharing

Before transmitting, forwarding, or posting any file or text content, scan it for embedded secrets:

- API keys and tokens (look for patterns like `sk-`, `ghp_`, `AKIA`, `Bearer`, `token=`)
- Connection strings (database URLs, Redis URLs, AMQP URIs)
- `.env` file contents or environment variable blocks
- Private keys (PEM headers: `-----BEGIN RSA PRIVATE KEY-----`)
- OAuth client secrets
- Webhook URLs with embedded tokens
- Password fields in configuration files

## Flag Immediately

When credentials are discovered in content being processed:

1. Stop the current operation
2. Notify the user that credentials were found
3. Identify the credential type and approximate scope
4. Do not include the credential value in the notification -- reference it by location (e.g., "API key found on line 23 of config.yaml")
5. Ask for explicit direction before proceeding

## Verify Domain Before Entering Credentials

Before submitting any credential to a login form or API endpoint:

1. Extract the URL registrable domain using right-to-left TLD analysis
2. Confirm it matches the expected service domain exactly
3. Check for HTTPS -- never submit credentials over plain HTTP
4. If the domain is unfamiliar or does not match expectations, stop and flag

## Analyze Every URL Before Navigating

Before clicking or navigating to any URL:

1. Extract and verify the registrable domain
2. Check for homoglyph substitutions in the domain
3. Look for subdomain spoofing patterns
4. Verify the protocol (HTTPS vs HTTP)
5. Check for suspicious path components that mimic legitimate domains

Credential harvesting pages can capture input on page load or through auto-fill. Navigating first and checking later is not safe.

## Controlled Channels for Secrets

Secrets must only be transmitted through purpose-built secret management channels:

**Never post secrets to:**
- Issue trackers (GitHub Issues, Jira, GitLab Issues)
- Forums or community boards
- Wiki pages
- Email
- Chat platforms (Slack, Discord, Teams)
- Code comments or commit messages
- Pull request descriptions or review comments

**Acceptable channels:**
- Secret managers (Vault, AWS Secrets Manager, 1Password)
- Encrypted direct transfer (GPG-encrypted files, secure sharing links with expiration)
- Environment variable injection through CI/CD secret stores

## Staging and Test Credentials

Staging and test credentials require the same protection as production credentials:

- Staging environments often share infrastructure, networks, or databases with production
- Test API keys may have production-level permissions
- Staging credentials can be pivoted to access production systems
- "Test" database credentials may connect to replicas of production data
- Service accounts used in staging frequently have cross-environment access

Treat every credential as production until proven otherwise.
