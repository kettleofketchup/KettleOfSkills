---
last_updated: "2026-03-18"
description: Discord webhooks — types, creation, execution, message management, Slack/GitHub compatibility
---

# Discord Webhooks Reference

## Webhook Types

| Type | Value | Description |
|------|-------|------------|
| Incoming | 1 | Post messages to channels with generated token |
| Channel Follower | 2 | Auto-republish messages from followed channels |
| Application | 3 | Associated with bot/OAuth2 app for interactions |

## Webhook Object

| Field | Type | Notes |
|-------|------|-------|
| id | snowflake | Unique ID |
| type | int | 1, 2, or 3 |
| guild_id | snowflake? | Source guild |
| channel_id | snowflake? | Target channel |
| user | object? | Creator (excluded with token auth) |
| name | string | 1-80 chars, cannot contain "clyde" or "discord" |
| avatar | string? | Avatar hash |
| token | string? | Incoming webhooks only |
| application_id | snowflake? | Owning application |
| url | string? | Execution URL |

## Creating Webhooks

```
POST /channels/{channel_id}/webhooks
```
Requires `MANAGE_WEBHOOKS` permission. Body: `name` (required), `avatar?` (image data).

## Executing Webhooks

```
POST /webhooks/{webhook_id}/{webhook_token}
```
No authentication required (token in URL).

**Query parameters:**
- `wait=true` — Returns created message object (default false)
- `thread_id` — Target specific thread
- `with_components=true` — Enable components for non-app webhooks

**Body** (must include at least one of content/embeds/components/file/poll):

| Field | Type | Notes |
|-------|------|-------|
| content | string | Max 2000 chars |
| username | string | Override webhook display name |
| avatar_url | string | Override avatar |
| tts | bool | Text-to-speech |
| embeds | array | Up to 10 embeds |
| allowed_mentions | object | Control mentions |
| components | array | Interactive/display components |
| files | array | Attachment contents |
| attachments | array | Partial attachment objects |
| flags | int | SUPPRESS_EMBEDS, SUPPRESS_NOTIFICATIONS, IS_COMPONENTS_V2 |
| thread_name | string | Auto-create thread (forum/media channels) |
| applied_tags | array | Forum tag IDs |
| poll | object | Poll request |

## Message Operations

**Get message:**
```
GET /webhooks/{id}/{token}/messages/{msg_id}
```

**Edit message:**
```
PATCH /webhooks/{id}/{token}/messages/{msg_id}
```
Mentions reconstructed from new content. Files appended unless `attachments` array specifies otherwise.

**Delete message:**
```
DELETE /webhooks/{id}/{token}/messages/{msg_id}
```

## Webhook CRUD

**Retrieve:**
```
GET /channels/{channel_id}/webhooks          (channel webhooks)
GET /guilds/{guild_id}/webhooks              (guild webhooks)
GET /webhooks/{id}                           (requires MANAGE_WEBHOOKS)
GET /webhooks/{id}/{token}                   (no auth needed)
```

**Modify:**
```
PATCH /webhooks/{id}                         (requires MANAGE_WEBHOOKS)
PATCH /webhooks/{id}/{token}                 (no auth, cannot change channel)
```

**Delete:**
```
DELETE /webhooks/{id}                        (requires MANAGE_WEBHOOKS)
DELETE /webhooks/{id}/{token}                (no auth needed)
```

## Compatibility Endpoints

**Slack format:**
```
POST /webhooks/{id}/{token}/slack
```

**GitHub format:**
```
POST /webhooks/{id}/{token}/github
```
Supported events: commit_comment, create, delete, fork, issues, pull_request, push, release, and more.

## Key Notes

- Webhooks do not require bot user or authentication (token-based)
- Embed `type`, `provider`, `video`, dimension/proxy fields unsupported
- Forum/media channels require `thread_id` or `thread_name`
- All modification/deletion triggers `Webhooks Update` gateway event
- Supports `X-Audit-Log-Reason` header for audit logging
