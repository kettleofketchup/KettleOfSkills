---
description: module.json and system.json manifest format, all fields, package directory structure
last_updated: 2026-03-18
---

# Package Manifests

## module.json - Required Fields

| Field | Description |
|-------|-------------|
| `id` | Lowercase with hyphens, must match folder name. No underscores or special chars |
| `title` | Human-readable display name |
| `description` | HTML-supported description |
| `version` | Semver string (e.g., "1.2.3") |

## module.json - Key Optional Fields

```json
{
  "id": "my-module",
  "title": "My Module",
  "description": "A module that does things",
  "version": "1.0.0",
  "compatibility": {
    "minimum": 12,
    "verified": "13",
    "maximum": "13"
  },
  "authors": [
    { "name": "Author", "discord": "user#0000", "url": "https://..." }
  ],
  "esmodules": ["scripts/main.mjs"],
  "scripts": ["scripts/legacy.js"],
  "styles": ["styles/module.css"],
  "languages": [
    { "lang": "en", "name": "English", "path": "lang/en.json" }
  ],
  "packs": [
    {
      "name": "my-items",
      "label": "My Items",
      "type": "Item",
      "system": "dnd5e",
      "path": "./packs/my-items",
      "ownership": { "PLAYER": "OBSERVER", "ASSISTANT": "OWNER" }
    }
  ],
  "packFolders": [
    { "name": "My Pack Folder", "sorting": "a", "packs": ["my-items"] }
  ],
  "relationships": {
    "systems": [{ "id": "dnd5e", "type": "system" }],
    "requires": [{ "id": "lib-wrapper", "type": "module" }]
  },
  "socket": true,
  "library": false,
  "url": "https://github.com/...",
  "manifest": "https://github.com/.../module.json",
  "download": "https://github.com/.../release/module.zip",
  "bugs": "https://github.com/.../issues",
  "changelog": "https://github.com/.../blob/main/CHANGELOG.md",
  "media": [
    { "type": "setup", "url": "modules/my-module/cover.webp" }
  ]
}
```

## system.json - Additional Fields

Systems have all module fields plus:

| Field | Description |
|-------|-------------|
| `documentTypes` | Custom Actor/Item sub-types |
| `grid` | Default distance and units |
| `primaryTokenAttribute` | Token bar 1 path (needs value/max) |
| `secondaryTokenAttribute` | Token bar 2 path |
| `initiative` | Default initiative formula (e.g., "1d20") |

```json
{
  "documentTypes": {
    "Actor": { "hero": {}, "villain": {}, "npc": {} },
    "Item": { "weapon": {}, "spell": {}, "armor": {} }
  },
  "grid": { "distance": 5, "units": "ft" },
  "primaryTokenAttribute": "resources.health",
  "secondaryTokenAttribute": "resources.power",
  "initiative": "1d20 + @abilities.dex.mod"
}
```

## esmodules vs scripts

- **esmodules** (preferred): ES6 modules with `import`/`export`. Each file is its own scope
- **scripts**: Legacy global-scope JS. Loaded in declared order. Avoid for new development

## Directory Structure

```
modules/my-module/         # or systems/my-system/
├── module.json            # system.json for systems
├── scripts/
│   └── main.mjs           # Entry point
├── module/                # Organized source code
│   ├── documents.mjs      # Custom document classes
│   ├── data-models.mjs    # TypeDataModel definitions
│   └── sheets/
│       ├── actor-sheet.mjs
│       └── item-sheet.mjs
├── templates/
│   ├── actor-sheet.hbs
│   └── item-sheet.hbs
├── styles/
│   └── module.css
├── packs/                 # Compendium data (LevelDB format v10+)
├── lang/
│   └── en.json
└── assets/                # Images, icons, etc.
```

## Localization (lang/en.json)

```json
{
  "MYMOD.settingName": "My Setting",
  "MYMOD.settingHint": "Configure this setting",
  "MYMOD.sheetTitle": "Character Sheet",
  "MYMOD.tabs.attributes": "Attributes"
}
```

Access in JS: `game.i18n.localize("MYMOD.settingName")`
Access in Handlebars: `{{localize "MYMOD.sheetTitle"}}`

## Compendium Packs

v10+ uses LevelDB format (folder-based). Pack `type` must be one of:
Actor, Item, Scene, JournalEntry, RollTable, Macro, Playlist, Adventure, Cards

Actor/Item/Adventure packs MUST specify `system` field.

## Validation

Always validate module.json with jsonlint.com before deployment. Invalid JSON prevents module loading with no error in UI.
