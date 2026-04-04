# API Keys

API keys are personal access tokens that let external code call the same endpoints the web UI uses. Each key inherits the permissions of the user who created it.

## Key Features

- **Bearer token auth**: Standard `Authorization: Bearer` header, works with any HTTP client or SDK
- **Scoped to user**: Key inherits the creating user's role and group permissions
- **Endpoint restrictions**: Optionally limit which API routes a key can access
- **Permission-gated**: Requires a global admin toggle plus per-group feature permission for non-admins

## Getting Started

### Step 1: Enable API Keys Globally (Admin)

1. Log in as an administrator
2. Open **Admin Panel > Settings > General**
3. Scroll to the **Authentication** section
4. Toggle **Enable API Keys** on
5. Click **Save**

This is the global master switch. When off, no one can generate keys. When on, admins can generate keys immediately; non-admins still need the feature permission.

(Optional) Enable **API Key Endpoint Restrictions** and specify allowed endpoints as a comma-separated list (e.g., `/api/v1/models,/api/v1/chat/completions`).

### Step 2: Grant Permission to Non-admin Users (Admin)

#### Option A: Default Permissions (all users)

1. **Admin Panel > Users > Groups > Default Permissions**
2. Under **Features Permissions**, toggle **API Keys** on
3. Click **Save**

#### Option B: User Groups (specific users)

1. **Admin Panel > Users > Groups**
2. Select or create a group (e.g., "API Users")
3. Under **Permissions > Features Permissions**, toggle **API Keys** on
4. Click **Save**

### Step 3: Generate a Key

1. Click your **profile icon** (bottom-left sidebar)
2. Select **Settings > Account**
3. In the **API Keys** section, click **Generate New API Key**
4. Give it a descriptive name (e.g., "Monitoring Bot")
5. **Copy the key immediately** - you won't be able to view it again

## Using Your API Key

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8080/api/models
```

```python
import requests

response = requests.get(
    "http://localhost:8080/api/models",
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
print(response.json())
```

## Best Practices

### Dedicated service accounts

Create a non-admin user specifically for automation (e.g., `monitoring-bot`, `ci-pipeline`). If a key leaks, the attacker only gets that user's permissions.

### Endpoint restrictions

Enable **API Key Endpoint Restrictions** and whitelist only the routes your integration needs. A monitoring bot only needs `/api/models` and `/api/chat/completions`.

### Key rotation

Periodically delete old keys and generate new ones. Name keys with a date or version to track rotation (`"Monitoring Bot - 2025-Q1"`).

## Troubleshooting

**Can't see the API Keys section in Settings > Account?**
- Check the global toggle: **Admin Panel > Settings > General > Enable API Keys** (`ENABLE_API_KEYS`)
- Check permissions (non-admin): Verify the **API Keys** feature permission (`USER_PERMISSIONS_FEATURES_API_KEYS`)

**Getting `401 Unauthorized` responses?**
- Verify format: `Authorization: Bearer sk-...`
- Check key hasn't been deleted
- If endpoint restrictions are enabled, confirm the route is in the allowlist

## Limitations

- **No post-creation viewing**: Keys cannot be viewed after creation. Delete and regenerate if lost.
- **No per-key permissions**: Keys inherit full permissions of the owner (beyond endpoint restrictions).
- **No automatic expiration**: Keys do not expire. Manually delete and rotate them.
