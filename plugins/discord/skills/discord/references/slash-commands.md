---
last_updated: "2026-03-18"
description: Discord application commands — types, options, registration, permissions, subcommands, autocomplete
---

# Slash Commands (Application Commands)

## Command Types

| Type | Value | Invocation |
|------|-------|-----------|
| CHAT_INPUT | 1 | `/command` in message box |
| USER | 2 | Right-click user → Apps |
| MESSAGE | 3 | Right-click message → Apps |
| PRIMARY_ENTRY_POINT | 4 | Activity launcher |

USER/MESSAGE commands: no description allowed, no options/parameters.

## Command Structure

| Field | Type | Notes |
|-------|------|-------|
| id | snowflake | Auto-assigned |
| name | string | 1-32 chars, regex `^[-_'\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$` |
| description | string | 1-100 chars (empty for USER/MESSAGE) |
| type | int | Default CHAT_INPUT |
| options | array | Max 25 (CHAT_INPUT only) |
| default_member_permissions | string | Bitwise OR permission string |
| nsfw | bool | Age-restricted |
| contexts | array | Interaction context types |
| integration_types | array | Installation contexts |

**Size limit:** 8000 chars total across name + description + all option values.

## Option Types

| Type | Value | Notes |
|------|-------|-------|
| SUB_COMMAND | 1 | Subcommand |
| SUB_COMMAND_GROUP | 2 | Groups subcommands |
| STRING | 3 | min/max_length 0-6000 |
| INTEGER | 4 | -2^53+1 to 2^53-1, min/max_value |
| BOOLEAN | 5 | |
| USER | 6 | Guild member |
| CHANNEL | 7 | Includes categories, filterable |
| ROLE | 8 | |
| MENTIONABLE | 9 | Users and roles |
| NUMBER | 10 | Double precision float, min/max_value |
| ATTACHMENT | 11 | File upload |

## Option Structure

| Field | Type | Notes |
|-------|------|-------|
| type | int | Required |
| name | string | 1-32 chars, unique within command |
| description | string | 1-100 chars |
| required | bool | Default false |
| choices | array | Max 25 predefined values |
| autocomplete | bool | Incompatible with choices |
| min_value/max_value | number | INTEGER/NUMBER only |
| min_length/max_length | int | STRING only, 0-6000 |
| channel_types | array | CHANNEL only filter |

## Subcommand Nesting

Valid structures (max 1 level deep):
```
command → subcommands
command → subcommand_groups → subcommands
```

Using subcommands makes the base command unusable.

## Registration

**Global commands** (propagation delay up to 1 hour):
```
POST /applications/{app_id}/commands
```
Limits: 100 CHAT_INPUT, 15 USER, 15 MESSAGE.

**Guild commands** (instant, for testing):
```
POST /applications/{app_id}/guilds/{guild_id}/commands
```
Same per-guild limits. Rate limit: 200 creates/day/guild.

**Bulk overwrite:**
```
PUT /applications/{app_id}/commands
PUT /applications/{app_id}/guilds/{guild_id}/commands
```

**CRUD:**
```
GET    /applications/{app_id}/commands
PATCH  /applications/{app_id}/commands/{cmd_id}
DELETE /applications/{app_id}/commands/{cmd_id}
```

## Permissions

**default_member_permissions**: Set at creation. `"0"` = admin-only.

**Per-guild overrides** (up to 100 users/roles/channels):
```
GET /applications/{app_id}/guilds/{guild_id}/commands/{cmd_id}/permissions
PUT /applications/{app_id}/guilds/{guild_id}/commands/{cmd_id}/permissions
```
Requires Bearer token (not bot token).

Permission types: ROLE (1), USER (2), CHANNEL (3).
`@everyone` = use guild_id as ID. All Channels = guild_id - 1.

## Autocomplete

- Set `autocomplete: true` on option (incompatible with `choices`)
- Receive `APPLICATION_COMMAND_AUTOCOMPLETE` interaction
- User's current input marked `focused: true`
- Respond with `APPLICATION_COMMAND_AUTOCOMPLETE_RESULT` (max 25 choices)
- Users can submit values not in suggestions

## Localization

Fields supporting localization: `name_localizations`, `description_localizations` on commands, options, and choices.

Locale fallbacks: en-US ↔ en-GB, es-419 → es-ES.

## Authorization

- Bot token: `Authorization: Bot <token>`
- Bearer token: `Authorization: Bearer <token>` (permissions endpoints)
- Scope: `applications.commands` (included with `bot` scope)
