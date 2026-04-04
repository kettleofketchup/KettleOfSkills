# SCIM 2.0 Support

Open WebUI supports SCIM 2.0 (System for Cross-domain Identity Management) for automated user and group provisioning from identity providers like Okta, Azure AD, and Google Workspace.

## Overview

When enabled, your identity provider can automatically:
- Create users in Open WebUI when they're added to your organization
- Update user information when changes are made
- Deactivate users when they're removed
- Manage group memberships

## Configuration

SCIM is configured entirely through environment variables. There is no UI configuration.

### Environment Variables

- **`SCIM_ENABLED`**: Set to `true` to enable SCIM support (default: `false`)
- **`SCIM_TOKEN`**: The bearer token for SCIM authentication (required when SCIM is enabled)
- **`SCIM_AUTH_PROVIDER`**: The OAuth provider name to associate with SCIM `externalId` values (e.g., `microsoft`, `oidc`). Required for `externalId` storage and account linking.

Generate a secure token:

```bash
openssl rand -base64 32
```

### Example Configuration

```bash
export SCIM_ENABLED=true
export SCIM_TOKEN="your-secure-token-here"
export SCIM_AUTH_PROVIDER="microsoft"
```

## SCIM API Configuration

- **SCIM Base URL**: `<your-openwebui-url>/api/v1/scim/v2/`
- **Authentication**: Bearer Token
- **Token**: `Bearer <your-scim-token>`

### Okta Setup

1. In Okta, add the SCIM application
2. Set SCIM connector base URL to: `https://your-domain.com/api/v1/scim/v2/`
3. Set authentication to "HTTP Header"
4. Add Authorization header with value: `Bearer your-scim-token`

## Supported SCIM Operations

### User Operations

| Operation | Endpoint |
|---|---|
| Create User | `POST /Users` |
| Get User | `GET /Users/{id}` |
| Update User | `PUT /Users/{id}`, `PATCH /Users/{id}` |
| Delete User | `DELETE /Users/{id}` |
| List Users | `GET /Users` |

### Group Operations

| Operation | Endpoint |
|---|---|
| Create Group | `POST /Groups` |
| Get Group | `GET /Groups/{id}` |
| Update Group | `PUT /Groups/{id}`, `PATCH /Groups/{id}` |
| Delete Group | `DELETE /Groups/{id}` |
| List Groups | `GET /Groups` |

### User Attributes

- `userName`: The user's email address (required, unique)
- `name.givenName`: First name
- `name.familyName`: Last name
- `emails`: Email addresses (when multiple are provided, the entry marked `primary: true` is used)
- `active`: User status (active/inactive)
- `externalId`: External identifier from the identity provider

### Group Attributes

- `displayName`: Group name (required)
- `members`: Array of user members
- `externalId`: External identifier from the identity provider

## Filtering Support

```
GET /api/v1/scim/v2/Users?filter=userName eq "user@example.com"
GET /api/v1/scim/v2/Users?filter=externalId eq "abc-123"
GET /api/v1/scim/v2/Groups?filter=displayName eq "Engineering"
```

Supported filter operators: `eq`, `ne`, `co`, `sw`, `ew`, `pr`, `gt`, `ge`, `lt`, `le`

## externalId and Account Linking

When `SCIM_AUTH_PROVIDER` is configured, `externalId` values are stored per-provider in the user's `scim` JSON field:

```json
{
  "microsoft": { "external_id": "abc-123" },
  "okta": { "external_id": "def-456" }
}
```

- **User lookup by externalId**: Searches the `scim` field for a matching entry under the configured provider
- **OAuth fallback**: If no user is found by `externalId`, falls back to matching against OAuth `sub` values
- **Create and update**: The `externalId` is stored in the `scim` field and returned in responses

If `SCIM_AUTH_PROVIDER` is not set while SCIM is enabled, any operation that requires `externalId` returns a `500` error.

## Troubleshooting

1. **401 Unauthorized**: Verify `SCIM_ENABLED=true`, token matches `SCIM_TOKEN`, header format is `Bearer <token>`
2. **404 Not Found**: Verify base URL ends with `/api/v1/scim/v2/`
3. **User Creation Failures**: Ensure `userName` is a valid email, email/`externalId` not already in use
4. **500 Error on externalId Operations**: Verify `SCIM_AUTH_PROVIDER` is set correctly

### Testing SCIM Endpoints

```bash
# List users
curl -H "Authorization: Bearer your-scim-token" \
  https://your-domain.com/api/v1/scim/v2/Users

# Create a test user
curl -X POST \
  -H "Authorization: Bearer your-scim-token" \
  -H "Content-Type: application/scim+json" \
  -d '{
    "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
    "userName": "test@example.com",
    "externalId": "idp-user-id-123",
    "displayName": "Test User",
    "name": {"givenName": "Test", "familyName": "User"},
    "emails": [{"value": "test@example.com", "primary": true}],
    "active": true
  }' \
  https://your-domain.com/api/v1/scim/v2/Users
```

## Security Considerations

1. **Use HTTPS** in production to protect the bearer token
2. **Secure Token Storage**: Store the SCIM token securely and rotate periodically
3. **IP Allowlisting**: Consider restricting SCIM API access to your identity provider's IPs
4. **Audit Logging**: SCIM operations are logged for security auditing

## Limitations

- Custom schema extensions are not supported
- Bulk operations are not implemented
- ETags for resource versioning are not supported

## Integration with SSO

SCIM works best combined with SSO. Typical setup: SCIM for automated user provisioning + OIDC for user authentication.
