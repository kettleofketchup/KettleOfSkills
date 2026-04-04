---
last_updated: "2026-03-18"
description: Discord API component types, fields, constraints, and V2 layout components
---

# Discord Components Reference

## Component Type IDs

| Type | ID | Category | Context |
|------|----|----------|---------|
| Action Row | 1 | Layout | Messages/Modals |
| Button | 2 | Interactive | Messages |
| String Select | 3 | Interactive | Messages/Modals |
| Text Input | 4 | Interactive | Modals |
| User Select | 5 | Interactive | Messages/Modals |
| Role Select | 6 | Interactive | Messages/Modals |
| Mentionable Select | 7 | Interactive | Messages/Modals |
| Channel Select | 8 | Interactive | Messages/Modals |
| Section | 9 | Layout | Messages (V2) |
| Text Display | 10 | Content | Messages/Modals (V2) |
| Thumbnail | 11 | Content | Messages (V2) |
| Media Gallery | 12 | Content | Messages (V2) |
| File | 13 | Content | Messages (V2) |
| Separator | 14 | Layout | Messages (V2) |
| Container | 17 | Layout | Messages (V2) |
| Label | 18 | Layout | Modals |
| File Upload | 19 | Interactive | Modals |
| Radio Group | 21 | Interactive | Modals |
| Checkbox Group | 22 | Interactive | Modals |
| Checkbox | 23 | Interactive | Modals |

All interactive components require `custom_id` (string, 1-100 chars, unique per component).

## Button (Type 2)

| Field | Type | Notes |
|-------|------|-------|
| style | int | Required. See styles below |
| label | string | Max 80 chars |
| emoji | partial emoji | `{name, id, animated}` |
| custom_id | string | Required for non-link/premium |
| url | string | Required for link style, max 512 |
| sku_id | snowflake | Premium style only |
| disabled | bool | Default false |

**Button Styles:**

| Style | Value | Color | Required Field |
|-------|-------|-------|----------------|
| Primary | 1 | Blue | custom_id |
| Secondary | 2 | Grey | custom_id |
| Success | 3 | Green | custom_id |
| Danger | 4 | Red | custom_id |
| Link | 5 | Grey+icon | url |
| Premium | 6 | — | sku_id |

## Action Row (Type 1)

Container for interactive elements. Top-level only.
- Up to 5 buttons OR 1 select menu per row
- Cannot nest Action Rows

## Select Menus (Types 3-8)

Common fields for all select types:

| Field | Type | Notes |
|-------|------|-------|
| custom_id | string | 1-100 chars |
| placeholder | string | Max 150 chars |
| min_values | int | Default 1, range 0-25 |
| max_values | int | Default 1, max 25 |
| required | bool | Modals only, default true |
| disabled | bool | Messages only, default false |

**String Select (Type 3)** additional: `options` array (max 25).

Option structure: `label` (100), `value` (100), `description?` (100), `emoji?`, `default?`

**Auto-populated selects** (User/Role/Mentionable/Channel): `default_values` array.
Channel Select adds `channel_types` filter array.

Response data: `values` (array of strings or snowflakes) + `resolved` object.

## Text Input (Type 4) — Modals Only

| Field | Type | Notes |
|-------|------|-------|
| custom_id | string | 1-100 chars |
| style | int | 1=Short (single-line), 2=Paragraph (multi-line) |
| min_length | int | 0-4000 |
| max_length | int | 1-4000 |
| required | bool | Default true |
| value | string | Pre-filled, max 4000 |
| placeholder | string | Max 100 chars |

## Components V2 (flag: `1 << 15`)

Enable with `IS_COMPONENTS_V2` message flag (32768). Disables `content` and `embeds` fields.

- **Section (9)**: 1-3 Text Display children + 1 Button/Thumbnail accessory
- **Text Display (10)**: Markdown content with mentions/emoji
- **Thumbnail (11)**: Image accessory in Sections. Fields: `media`, `description?` (1024), `spoiler?`
- **Media Gallery (12)**: 1-10 gallery items with `media`, `description?`, `spoiler?`
- **Separator (14)**: Vertical spacing between components
- **Container (17)**: Groups components together

## Constraints Summary

- 40 components max per message
- Action Row: max 5 buttons or 1 select
- Select options: max 25
- custom_id: 1-100 chars, unique per component
- `disabled` cannot be used in modals
