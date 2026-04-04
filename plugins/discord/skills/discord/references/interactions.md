---
last_updated: "2026-03-18"
description: Discord interaction object structure, types, callback responses, endpoints, and security
---

# Discord Interactions Reference

## Interaction Object

| Field | Type | Notes |
|-------|------|-------|
| id | snowflake | Unique interaction ID |
| application_id | snowflake | Target application |
| type | int | See Interaction Types |
| token | string | Valid 15 minutes. Used for responses |
| version | int | Always 1 |
| data | object | Type-specific payload (absent for PING) |
| guild_id | snowflake? | Server context |
| channel_id | snowflake? | Channel context |
| member | object? | Guild member + permissions |
| user | object? | User object (DMs) |
| message | object? | Originating message (component/modal) |
| app_permissions | string | Bitwise permissions in source |
| locale | string? | User's language |
| guild_locale | string? | Server's language |
| entitlements | array | Monetization data |
| context | int? | 0=GUILD, 1=BOT_DM, 2=PRIVATE_CHANNEL |

## Interaction Types

| Type | Value | Trigger |
|------|-------|---------|
| PING | 1 | Server verification |
| APPLICATION_COMMAND | 2 | Slash/user/message command |
| MESSAGE_COMPONENT | 3 | Button or select menu click |
| APPLICATION_COMMAND_AUTOCOMPLETE | 4 | Autocomplete typing |
| MODAL_SUBMIT | 5 | Modal form submitted |

## Interaction Data by Type

**APPLICATION_COMMAND**: `id`, `name`, `type`, `options[]`, `resolved{}`, `target_id?`

**MESSAGE_COMPONENT**: `custom_id`, `component_type`, `values[]`, `resolved{}`

**MODAL_SUBMIT**: `custom_id`, `components[]`, `resolved{}`

**AUTOCOMPLETE**: Same as APPLICATION_COMMAND but `focused: true` on active option.

## Callback Response Types

| Type | Value | Use | Restrictions |
|------|-------|-----|-------------|
| PONG | 1 | Ack PING | PING only |
| CHANNEL_MESSAGE_WITH_SOURCE | 4 | Send message | — |
| DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE | 5 | "Thinking..." → editReply later | — |
| DEFERRED_UPDATE_MESSAGE | 6 | Ack without loading (components) | Components only |
| UPDATE_MESSAGE | 7 | Edit originating message | Components only |
| APPLICATION_COMMAND_AUTOCOMPLETE_RESULT | 8 | Return choices (max 25) | Autocomplete only |
| MODAL | 9 | Show modal form | Not MODAL_SUBMIT/PING |
| LAUNCH_ACTIVITY | 12 | Start Activity | Entry point only |

## Response Data Fields

| Field | Type | Notes |
|-------|------|-------|
| content | string | Message text |
| embeds | array | Up to 10 embeds |
| components | array | Buttons, selects, action rows |
| attachments | array | Files with metadata |
| allowed_mentions | object | Mention filtering |
| flags | int | EPHEMERAL (64), SUPPRESS_EMBEDS (4), IS_COMPONENTS_V2 (32768) |
| tts | bool | Text-to-speech |
| poll | object | Poll data |

## API Endpoints

**Initial response:**
```
POST /interactions/{id}/{token}/callback
```
Returns 204 (or 200 with `?with_response=true`).

**Edit/delete initial response:**
```
PATCH  /webhooks/{app_id}/{token}/messages/@original
DELETE /webhooks/{app_id}/{token}/messages/@original
```

**Followup messages:**
```
POST   /webhooks/{app_id}/{token}
PATCH  /webhooks/{app_id}/{token}/messages/{msg_id}
DELETE /webhooks/{app_id}/{token}/messages/{msg_id}
GET    /webhooks/{app_id}/{token}/messages/{msg_id}
```

## Critical Timing

- **3 seconds** to send initial response
- **15 minutes** token validity for edits/followups
- User-installed apps: max 5 followups per interaction

## Delivery Methods

1. **Gateway** (WebSocket): `INTERACTION_CREATE` event
2. **HTTP Webhook**: POST to configured Interactions Endpoint URL

HTTP interactions include `X-Signature-Ed25519` and `X-Signature-Timestamp` headers.
Validate with Ed25519 signature verification. PING requests respond with `{"type": 1}`.

## Resolved Data

The `resolved` object contains full objects for referenced entities:
- `users{}` — User objects keyed by ID
- `members{}` — Member objects (no `user`/`deaf`/`mute`)
- `roles{}` — Role objects
- `channels{}` — Partial channel objects
- `messages{}` — Partial message objects
- `attachments{}` — Attachment objects
