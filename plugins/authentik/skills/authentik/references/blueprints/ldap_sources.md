# LDAP Sources — Matching Modes, Password Sync, Field Reference

LDAP sources adopt directory users into authentik. The matching mode determines whether sync creates duplicates, links to existing rows, or denies. The password sync field determines whether offline auth fallback works. Get either wrong and users either can't log in or get duplicated.

## user_matching_mode (critical)

Field on `LDAPSource`. Controls what happens during sync when an incoming LDAP user is processed by `authentik/core/sources/matcher.py`. Match order:

1. Existing `UserSourceConnection` by `(source, identifier=object_uniqueness_field)` → `Action.AUTH` (update attrs)
2. Legacy `attributes.ldap_uniq` adoption (only for users that previously had `ldap_uniq` set)
3. Falls through to `user_matching_mode`:

| Mode | Behavior on first sync against pre-existing row |
|------|-------------------------------------------------|
| `identifier` (default) | **Always creates a new user** if no source connection exists. Will produce **duplicates** when blueprints have pre-created rows. ❌ |
| `username_link` | If a user with matching `username` exists, create a `UserSourceConnection` linking them, run `update_attributes(defaults)`. ✅ Correct for blueprint-preseeded users. |
| `username_deny` | If username clashes, deny the import (`Action.DENY`). |
| `email_link` | Match by `email`. **Insecure** if source doesn't validate email — explicitly flagged in upstream enum help text. |
| `email_deny` | Deny on email clash. |

**Always use `username_link`** when you pre-create user rows via blueprint. The `path` you assigned is irrelevant to matching — only the `username` field matches.

## group_matching_mode

Same enum, applied to groups. Values: `identifier`, `name_link`, `name_deny`. Use `name_link` for the same reason — it lets blueprint-declared groups be adopted by LDAP sync without duplication.

Membership reconciliation in `authentik/sources/ldap/sync/membership.py`: LDAP sync sets the user's groups to **match AD's view**, but **only for groups linked via `GroupSourceConnection`**. Blueprint-added memberships to authentik-native groups (groups not linked to the LDAP source) are preserved across sync runs. So our admin-group bindings via `!Find` against `authentik_core.user` are safe — sync won't clobber them unless the group itself is also LDAP-synced.

## password_login_update_internal_password

Field name on `LDAPSource` (OSS, not enterprise). Default: `False`. Set to `True` to enable offline LDAP auth fallback.

**What it does** (see `authentik/sources/ldap/auth.py LDAPBackend.auth_user`): On each successful LDAP bind during a login, authentik takes the **already-validated plaintext** from request memory and calls `user.set_password(plaintext) → save()`. Django hashes it (PBKDF2-SHA256 default, Argon2 if configured) and writes to the local `password` column.

**What it does NOT do**: Pull `unicodePwd`, NTLM hashes, Samba password attributes, or any cleartext from AD via the directory protocol. There is no replication. There is no bulk backfill. Each user's offline credential populates lazily on their next interactive LDAP login.

**Plaintext at rest? No.** Plaintext exists only in request handler memory for one HTTP request — same as any password form anywhere. What's persisted is a strong KDF hash.

**AD-specific gotcha**: For AD and FreeIPA, authentik **invalidates** the locally-stored hash on the next LDAP sync poll (sets `password` to an unusable marker). The offline window is `[last successful login] → [next sync run]`. For pure OpenLDAP, the hash persists indefinitely. Document this trade-off when deploying — users won't be able to log in if AD is unreachable AND the last sync ran more recently than their last login.

**Why this design**: Pulling actual AD hashes would require DRSGetNCChanges replication permissions (DC-equivalent privileges), and AD's stored hashes are MD4-based NTLM (much weaker than PBKDF2/Argon2). Authentik's approach mirrors PAM/sssd's offline cache — capture-on-bind, hash locally with a strong KDF, no special directory privileges needed.

## delete_not_found_objects

Field on `LDAPSource`. Default: `False`. When `True`, the next sync poll will delete locally-cached users and groups that no longer exist in AD's response. LDAP becomes the source of truth.

**Safety note**: Only deletes users/groups that have a `UserSourceConnection`/`GroupSourceConnection` to this LDAP source. Blueprint-preseeded rows that have not yet been adopted by sync (`connections=0`) are **not** touched. Native authentik users (e.g. `akadmin`) are never deleted by an LDAP source.

Set this to `True` when you want strict directory-as-source-of-truth. Leave it `False` if you have local-only authentik users that should survive even if their AD account is removed.

## Other relevant LDAPSource fields

| Field | Notes |
|-------|-------|
| `server_uri` | Use `ldaps://` or set `start_tls: true` for protected binds — plaintext binds expose passwords on the wire |
| `bind_cn` / `bind_password` | Service account for sync queries. Read-only is sufficient |
| `base_dn` | Top of the search tree |
| `additional_user_dn` / `additional_group_dn` | Subtree filters appended to base_dn |
| `user_object_filter` | LDAP filter for what counts as a user. AD: `(&(objectCategory=person)(objectClass=user))` |
| `group_object_filter` | LDAP filter for groups. AD: `(objectClass=group)` |
| `object_uniqueness_field` | Stable identifier for `UserSourceConnection`. AD: `objectSid` |
| `sync_users` / `sync_groups` | Enable user/group sync passes independently |
| `sync_parent_group` | Optional umbrella group all synced users get added to |

## How to verify sync state

```python
# In `kubectl exec deploy/authentik-server -- ak shell`
from authentik.sources.ldap.models import LDAPSource, UserLDAPSourceConnection
from authentik.core.models import User

src = LDAPSource.objects.get(slug="<your-slug>")
print(f"enabled={src.enabled} sync_users={src.sync_users}")
print(f"user_matching_mode={src.user_matching_mode}")
print(f"password_login_update_internal_password={src.password_login_update_internal_password}")
print(f"delete_not_found_objects={src.delete_not_found_objects}")

u = User.objects.get(username="<some_user>")
print(f"path={u.path}")
print(f"has_usable_password={u.has_usable_password()}")  # False = no offline cred
print(f"attrs={list((u.attributes or {}).keys())}")      # empty = sync hasn't touched
print(f"connections={UserLDAPSourceConnection.objects.filter(user=u).count()}")
# connections=0 means LDAP sync has NEVER adopted this user
```

If `connections=0` and you've waited past one sync interval, the sync isn't reaching the directory. Check worker logs for `authentik.sources.ldap.tasks.ldap_sync` task results, network reachability from the worker pod to `server_uri`, and bind credentials.

## Manually triggering a sync

```bash
kubectl exec deploy/authentik-worker -- ak ldap_sync <source-slug>
```

The CLI may fail with `dramatiq.results.errors.ResultMissing` when trying to retrieve the result — that's harmless, the task is enqueued and runs async on the worker. Verify completion via the worker logs or by re-checking user state in the shell after a minute.
