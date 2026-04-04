---
last_updated: "2026-03-18"
description: Discord embed structure, field limits, allowed mentions, and message flags
---

# Discord Embeds & Message Formatting

## Embed Structure

| Field | Type | Limit | Notes |
|-------|------|-------|-------|
| title | string | 256 chars | |
| description | string | 4096 chars | |
| url | string | — | Makes title clickable |
| color | int | — | Decimal color value |
| timestamp | ISO8601 | — | Adjusts to user timezone |
| footer | object | text: 2048 | `{text, icon_url}` |
| author | object | name: 256 | `{name, url, icon_url}` |
| thumbnail | object | — | `{url}` small top-right image |
| image | object | — | `{url}` large image |
| fields | array | 25 max | See below |

### Field Object

| Field | Type | Limit |
|-------|------|-------|
| name | string | 256 chars (required) |
| value | string | 1024 chars (required) |
| inline | bool | Side-by-side display |

Inline fields need 2+ consecutive to display side-by-side. Use `\u200B` (zero-width space) for blank fields.

## Embed Limits

| Constraint | Limit |
|-----------|-------|
| Embeds per message | 10 |
| Total chars (title + description + field.name + field.value + footer.text + author.name) | 6000 across ALL embeds |
| Fields per embed | 25 |

## Allowed Mentions Object

Controls which mentions trigger notifications.

```json
{
  "parse": ["users", "roles", "everyone"],
  "users": ["123456789"],
  "roles": ["987654321"],
  "replied_user": true
}
```

| Field | Type | Notes |
|-------|------|-------|
| parse | array | Mention types to parse: `users`, `roles`, `everyone` |
| users | array | Specific user IDs to allow (max 100) |
| roles | array | Specific role IDs to allow (max 100) |
| replied_user | bool | Whether to ping replied user |

**Default behavior differs by context:**
- Regular messages: parse all types
- Interactions & webhooks: parse only user mentions

`parse` and explicit ID arrays are mutually exclusive per type.

## Message Flags (Bot-Relevant)

| Flag | Value | Hex | Description |
|------|-------|-----|------------|
| SUPPRESS_EMBEDS | 1 << 2 | 0x4 | Hide embeds |
| EPHEMERAL | 1 << 6 | 0x40 | Only visible to invoker (interactions only) |
| SUPPRESS_NOTIFICATIONS | 1 << 12 | 0x1000 | No push notifications |
| IS_VOICE_MESSAGE | 1 << 13 | 0x2000 | Voice message |
| IS_COMPONENTS_V2 | 1 << 15 | 0x8000 | Enable V2 components (disables content/embeds) |

## Message Types (Bot Context)

| Type | Value | Description |
|------|-------|------------|
| DEFAULT | 0 | Standard message |
| REPLY | 19 | Reply to another message |
| CHAT_INPUT_COMMAND | 20 | Slash command response |
| CONTEXT_MENU_COMMAND | 23 | Context menu response |

## Embed JSON Example

```json
{
  "embeds": [{
    "title": "Status Update",
    "description": "Service is **operational**",
    "color": 5763719,
    "fields": [
      {"name": "Region", "value": "US-East", "inline": true},
      {"name": "Uptime", "value": "99.9%", "inline": true}
    ],
    "footer": {"text": "Last checked"},
    "timestamp": "2026-03-18T12:00:00.000Z",
    "thumbnail": {"url": "https://example.com/icon.png"}
  }]
}
```

## Color Values

Common colors (decimal):
- Blurple: 5793266 (0x5865F2)
- Green: 5763719 (0x57F287)
- Yellow: 16705372 (0xFEE75C)
- Fuchsia: 15418782 (0xEB459E)
- Red: 15548997 (0xED4245)
- White: 16777215 (0xFFFFFF)
- Black: 2303786 (0x23272A)
