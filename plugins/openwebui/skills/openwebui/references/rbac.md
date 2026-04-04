# Role-Based Access Control (RBAC)

Open WebUI implements RBAC through three interconnected layers:

1. **Roles**: The high-level user type (Admin, User, Pending). Defines baseline trust level.
2. **Permissions**: Granular feature flags (e.g., "Can Delete Chats", "Can Use Web Search").
3. **Groups**: Mechanism for organizing users, granting additional permissions, and managing shared access to resources (ACLs). Resources can also be shared directly to individual users.

**Key Concept: Additive Permissions** - Users start with their default rights, and Group memberships add capabilities. A user effectively has the union of all rights granted by their Roles and Groups. There is no "Deny" ability.

## How It Fits Together

1. Users authenticate via SSO, OIDC, LDAP, or local credentials
2. SCIM provisions users and groups automatically from your identity provider
3. RBAC determines access based on roles (Admin, User) and group memberships
4. Permissions are additive: each group membership adds capabilities, never removes them
5. API keys inherit the creating user's full permissions for programmatic access

### Per-Resource Access Control

Models, Knowledge bases, Tools, and Skills all support fine-grained access control. Resources are private by default. The creator controls who can see and use them via user grants, group grants, or public visibility.

## Roles

| Role | Keyword | Description |
|---|---|---|
| **Admin** | `admin` | Superuser. Full control over the system. |
| **User** | `user` | Standard User. Subject to RBAC permissions. |
| **Pending** | `pending` | Restricted. No access until approved. |

### Administrator (`admin`)

- **Full Access**: Default access to all resources and settings
- **Management**: Can manage users, groups, and global configurations
- **Bypass**: Bypasses most permission checks by default

**Admin Limitations:**
- `ENABLE_ADMIN_CHAT_ACCESS=False` can prevent Admins from viewing user chats
- If `BYPASS_ADMIN_ACCESS_CONTROL` is disabled, Admins may require explicit permissions to access private model/knowledge/notes resources
- Admins can generate API keys whenever `ENABLE_API_KEYS` is enabled

### Standard User (`user`)

Does not have implicit access. All capabilities must be granted via Global Default Permissions or Group Memberships. Effective rights are the sum of all grants.

### Pending User (`pending`)

Zero access. Cannot perform any actions. Must be promoted to `user` or `admin` by an administrator.

The `admin` role effectively has `check_permission() == True` for everything. Granular permissions generally do not apply to admins.

### Role Assignment

- **First User**: The first account created is automatically assigned Admin
- **Headless Admin Creation**: Use environment variables for automated deployments (see below)
- **Subsequent Users**: Assigned the `DEFAULT_USER_ROLE`

```bash
DEFAULT_USER_ROLE=pending
# Options: 'pending', 'user', 'admin'
```

Administrators can change roles at any time via **Admin Panel > Users**.

### Headless Admin Account Creation

For automated deployments where manual interaction is impractical:

- `WEBUI_ADMIN_EMAIL`: The admin account email address
- `WEBUI_ADMIN_PASSWORD`: The admin account password
- `WEBUI_ADMIN_NAME`: (Optional) Display name (defaults to "Admin")

Behavior: Only creates the admin if no users exist in the database (fresh install). Password is securely hashed. Signup is automatically disabled after creation. One-time operation on first startup.

#### Docker Compose Example

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - WEBUI_ADMIN_EMAIL=admin@example.com
      - WEBUI_ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - WEBUI_ADMIN_NAME=System Administrator
```

#### Kubernetes Secret Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openwebui-admin
type: Opaque
stringData:
  admin-email: admin@example.com
  admin-password: your-secure-password
  admin-name: System Administrator
---
apiVersion: v1
kind: Pod
metadata:
  name: open-webui
spec:
  containers:
  - name: open-webui
    image: ghcr.io/open-webui/open-webui:main
    env:
    - name: WEBUI_ADMIN_EMAIL
      valueFrom:
        secretKeyRef:
          name: openwebui-admin
          key: admin-email
    - name: WEBUI_ADMIN_PASSWORD
      valueFrom:
        secretKeyRef:
          name: openwebui-admin
          key: admin-password
    - name: WEBUI_ADMIN_NAME
      valueFrom:
        secretKeyRef:
          name: openwebui-admin
          key: admin-name
```

## Groups

Groups serve two primary purposes:
1. **Permission Management:** Assigning granular permissions to multiple users efficiently
2. **Resource Access Control:** Controlling who can access specific private resources (Models, Knowledge Bases, Tools)

**Permission Merging Logic:** Permissions are additive (Union-based). If a user is in multiple groups, they receive the superset of all permissions. "Deny" permissions do not exist.

### Group Configuration

**Who can share to this group** (Access Control setting):
- **Anyone**: (Default) Any user can see this group in sharing menus
- **Members**: Only group members see it in sharing menus
- **No one**: Hidden from sharing menus for non-admins (use for RBAC-only groups)

**Strategy: Permission Groups vs. Sharing Groups:**
- **Permission Groups** (prefix `[Perms]`): For granting features. Set "Who can share" to No one. Disable all sharing.
- **Sharing Groups** (prefix `Team-`): For organizing people. Set "Who can share" to Members/Anyone. Disable all permissions. Rely on Global Defaults for feature rights.

### Creation Methods

- **Manual Creation:** Via Admin Panel > Groups
- **OAuth Synchronization:** With `ENABLE_OAUTH_GROUP_MANAGEMENT`, groups sync from OAuth provider. `ENABLE_OAUTH_GROUP_CREATION` auto-creates missing groups.

### Resource Access (ACLs)

1. Set resource visibility to Private or Restricted
2. Grant access to specific Groups or individual users with Read or Write permission

Access grants are stored as normalized entries with Resource (type + ID), Principal (group or user), and Permission (read or write). Public access uses a wildcard (`*`) principal.
