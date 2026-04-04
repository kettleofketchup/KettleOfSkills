---
name: discord
description: Discord API interactions, message components, slash commands, modals, webhooks, and embeds. Use when building Discord bots, creating slash commands (application commands), adding interactive components (buttons, select menus, text inputs), implementing modal forms, sending webhook messages, constructing rich embeds, handling interaction responses (defer, reply, followup, edit), registering global/guild commands, configuring command permissions, or working with discord.py (Python) and discord.js (TypeScript/JavaScript) libraries.
---

# Discord API Interactions

Build Discord bots with interactive components, slash commands, modals, and webhooks.

## When to Use

Activate when working with:
- Slash commands (application commands) — registration, options, permissions
- Message components — buttons, select menus, action rows
- Modal dialogs — text inputs, form collection, file uploads
- Interaction responses — reply, defer, followup, edit, ephemeral
- Webhooks — sending messages, embeds, managing webhook messages
- Rich embeds — structured message formatting
- discord.py or discord.js library code

## Discord API References

Core API concepts and object structures from the official Discord developer docs.

| Reference | Content |
|-----------|---------|
| [Components](references/components.md) | All component types (buttons, selects, text inputs, V2 layout), fields, constraints |
| [Interactions](references/interactions.md) | Interaction object, types, callback types, response endpoints, security |
| [Slash Commands](references/slash-commands.md) | Command types, option types, registration, permissions, subcommands, autocomplete |
| [Modals](references/modals.md) | Modal structure, text inputs, selects, file uploads, submission handling |
| [Webhooks](references/webhooks.md) | Webhook types, execution, message CRUD, Slack/GitHub compatibility |
| [Embeds](references/embeds.md) | Embed structure, field limits, allowed mentions, message flags |

## Framework References

Library-specific patterns for the two most popular Discord bot frameworks.

### discord.py (Python)

| Reference | Content |
|-----------|---------|
| [Components](references/frameworks/discord-py/components.md) | Views, Buttons, Selects, Modals, TextInput, interaction callbacks |
| [Commands](references/frameworks/discord-py/commands.md) | app_commands, hybrid commands, tree.sync, groups, error handling |
| [Webhooks](references/frameworks/discord-py/webhooks.md) | Webhook class, sending embeds/files, editing/deleting messages |

### discord.js (TypeScript/JavaScript)

| Reference | Content |
|-----------|---------|
| [Components](references/frameworks/discord-js/components.md) | ButtonBuilder, SelectMenuBuilders, ModalBuilder, TextInputBuilder, LabelBuilder |
| [Commands](references/frameworks/discord-js/commands.md) | SlashCommandBuilder, response methods, options, subcommands, registering |
| [Webhooks & Embeds](references/frameworks/discord-js/webhooks.md) | WebhookClient, EmbedBuilder, sending/editing/deleting webhook messages |

## Quick Patterns

### Interaction Response Flow
```
User action → Interaction received → Must respond within 3s
  ├── reply()          → Immediate message
  ├── deferReply()     → "Thinking..." then editReply() within 15m
  ├── showModal()      → Open modal form (must be first response)
  ├── update()         → Edit originating message (components only)
  └── deferUpdate()    → Ack without visible change (components only)
```

### Component Limits
- 40 components max per message
- Action Row: 5 buttons OR 1 select menu
- Select menu: 25 options max, 0-25 selectable
- custom_id: 1-100 characters, unique per component
- Interaction token valid 15 minutes

### Embed Limits
- Title: 256 chars | Description: 4096 chars
- Fields: 25 max (name 256, value 1024)
- Footer: 2048 chars | Author name: 256 chars
- Total across all embeds: 6000 chars | Max 10 embeds/message
