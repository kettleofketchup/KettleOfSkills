---
last_updated: "2026-03-18"
description: Discord modal dialogs — structure, text inputs, select menus, file uploads, submission handling
---

# Discord Modals Reference

Modals are single-user pop-up forms triggered as an interaction response. Max 5 top-level components.

## Modal Structure

```json
{
  "type": 9,
  "data": {
    "custom_id": "my_modal",
    "title": "Form Title",
    "components": [...]
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| custom_id | string | 1-100 chars, identifies the modal |
| title | string | Displayed at top of modal |
| components | array | Max 5 top-level components |

## Modal Components

### Label (Type 18) — Recommended Wrapper

Wraps interactive components with context text.

| Field | Type | Notes |
|-------|------|-------|
| label | string | Header text, max 45 chars |
| description | string? | Subtext, max 100 chars |
| component | object | Single interactive component |
| required | bool | Default true |

### Text Input (Type 4)

| Field | Type | Notes |
|-------|------|-------|
| custom_id | string | 1-100 chars |
| style | int | 1=Short (single-line), 2=Paragraph (multi-line) |
| min_length | int? | 0-4000 |
| max_length | int? | 1-4000 |
| required | bool | Default true |
| value | string? | Pre-filled, max 4000 chars |
| placeholder | string? | Hint text, max 100 chars |

### String Select (Type 3) in Modals

Same as message select but with `required` field instead of `disabled`.
Options max 25, each with label/value/description/emoji/default.

### File Upload (Type 19)

| Field | Type | Notes |
|-------|------|-------|
| custom_id | string | 1-100 chars |
| required | bool | Default true |
| min_values | int | 0-10 |
| max_values | int | Max 10 |

File data not in interaction payload — download from Discord CDN.
Cannot validate file size or extension.

### Radio Group (Type 21)

Single-choice selection. Max 25 options.
Option: `label` (100), `value` (100), `description?` (100), `default?`

### Checkbox Group (Type 22)

Multi-choice selection. Max 25 options. Same option structure as Radio Group.

### Text Display (Type 10)

Read-only markdown content for additional context in modals.

## Triggering Modals

Modals **must be the first response** to an interaction. Cannot defer then show modal.

Respond with callback type `MODAL` (9):
```json
{
  "type": 9,
  "data": {
    "custom_id": "feedback_form",
    "title": "Submit Feedback",
    "components": [
      {
        "type": 18,
        "label": "What do you think?",
        "component": {
          "type": 4,
          "custom_id": "feedback_text",
          "style": 2,
          "placeholder": "Enter your feedback...",
          "min_length": 10,
          "max_length": 1000
        }
      }
    ]
  }
}
```

## Handling Submissions

Interaction type `MODAL_SUBMIT` (5) with data:

```json
{
  "type": 5,
  "data": {
    "custom_id": "feedback_form",
    "components": [
      {
        "type": 4,
        "custom_id": "feedback_text",
        "value": "User's input here"
      }
    ]
  }
}
```

Empty text inputs return empty string. Unselected select menus return empty array.

Valid responses to MODAL_SUBMIT: all callback types except MODAL (cannot chain modals).

## Restrictions

- Cannot show modal from another MODAL_SUBMIT interaction
- Cannot show modal from PING
- Must be first response (no deferring before modal)
- Max 5 top-level components
- Label component recommended over Action Row for text inputs
