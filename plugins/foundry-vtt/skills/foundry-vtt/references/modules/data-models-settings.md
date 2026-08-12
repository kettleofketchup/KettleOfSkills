---
description: Game Settings API registration and module-defined document sub-types (v11+)
last_updated: 2026-03-18
---

# Game Settings & Module Sub-Types

## Game Settings API

```javascript
// Register (in init hook)
game.settings.register("my-module", "difficulty", {
  name: "MYMOD.DifficultyName",
  hint: "MYMOD.DifficultyHint",
  scope: "world",        // GM-only setting
  config: true,          // Show in module settings
  type: String,
  choices: { easy: "Easy", normal: "Normal", hard: "Hard" },
  default: "normal",
  requiresReload: true   // Prompt reload on change
});

// Register client setting (per-user)
game.settings.register("my-module", "theme", {
  scope: "client",
  config: true,
  type: String,
  default: "dark"
});

// Read/Write (in ready hook or later)
const val = game.settings.get("my-module", "difficulty");
await game.settings.set("my-module", "difficulty", "hard");
```

### Setting Menus

```javascript
game.settings.registerMenu("my-module", "myMenu", {
  name: "MYMOD.SettingsMenuName",
  hint: "MYMOD.SettingsMenuHint",
  label: "Open Settings",
  icon: "fas fa-bars",
  type: MySettingsApplication,  // ApplicationV2 class
  restricted: true              // GM only
});
```

## Module-Defined Sub-Types (v11+)

Modules can extend Actor/Item types without being a system:

```json
{
  "id": "my-module",
  "documentTypes": {
    "Actor": { "companion": {} },
    "JournalEntryPage": { "encounter": {} }
  }
}
```

Register TypeDataModel for each declared sub-type:

```javascript
Hooks.once("init", () => {
  CONFIG.Actor.dataModels.companion = CompanionDataModel;
});
```

Sub-type actors/items work like system-defined types but are scoped to modules that have the module active.

## Flags

Per-document arbitrary data storage:

```javascript
// Set a flag
await actor.setFlag("my-module", "customData", { foo: "bar" });

// Get a flag
const data = actor.getFlag("my-module", "customData");

// Unset a flag
await actor.unsetFlag("my-module", "customData");
```

Flags are namespaced by module ID and stored in `document.flags["my-module"]`.

## Localization

```javascript
// Register i18n translations in module.json
// "languages": [{ "lang": "en", "name": "English", "path": "lang/en.json" }]

// en.json
{
  "MYMOD.DifficultyName": "Difficulty",
  "MYMOD.DifficultyHint": "Set the game difficulty level."
}

// Use in code
game.i18n.localize("MYMOD.DifficultyName");     // "Difficulty"
game.i18n.format("MYMOD.Greeting", { name: "Hero" }); // with substitution
```
