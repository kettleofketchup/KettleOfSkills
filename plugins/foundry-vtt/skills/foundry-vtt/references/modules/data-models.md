---
description: TypeDataModel schemas, field types, data preparation, migration, CONFIG registration
last_updated: 2026-03-18
---

# Data Models

## TypeDataModel (v10+)

Define structured schemas for Actor/Item sub-types using field classes:

```javascript
const fields = foundry.data.fields;

class HeroDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() {
    return {
      level: new fields.NumberField({
        required: true, integer: true, initial: 1, min: 1, max: 20
      }),
      experience: new fields.NumberField({ required: true, initial: 0, min: 0 }),
      resources: new fields.SchemaField({
        health: new fields.SchemaField({
          value: new fields.NumberField({ required: true, integer: true, initial: 10 }),
          max: new fields.NumberField({ required: true, integer: true, initial: 10 })
        }),
        mana: new fields.SchemaField({
          value: new fields.NumberField({ initial: 5 }),
          max: new fields.NumberField({ initial: 5 })
        })
      }),
      biography: new fields.HTMLField({ initial: "" }),
      alignment: new fields.StringField({ required: true, initial: "neutral", choices: ["lawful", "neutral", "chaotic"] }),
      abilities: new fields.SchemaField({
        str: new fields.SchemaField({
          value: new fields.NumberField({ initial: 10 }),
          mod: new fields.NumberField({ initial: 0 })
        })
        // ... repeat for dex, con, int, wis, cha
      }),
      isRetired: new fields.BooleanField({ initial: false })
    };
  }
}
```

## Available Field Types

| Field Class | Description |
|-------------|-------------|
| `NumberField` | Numeric (integer, min, max, step, positive, nullable) |
| `StringField` | String (blank, trim, choices, textSearch) |
| `BooleanField` | true/false |
| `HTMLField` | HTML string (sanitized) |
| `SchemaField` | Nested object with sub-fields |
| `ArrayField` | Array of a single field type |
| `SetField` | Set (unique array) of a field type |
| `ObjectField` | Freeform object (no schema) |
| `FilePathField` | File path with categories filter |
| `ColorField` | CSS color string (#hex) |
| `JSONField` | Serialized JSON string |
| `DocumentIdField` | Valid document ID reference |
| `EmbeddedDataField` | Embedded DataModel instance |

## Register Models

```javascript
Hooks.once("init", () => {
  // Actor sub-types
  CONFIG.Actor.dataModels.hero = HeroDataModel;
  CONFIG.Actor.dataModels.villain = VillainDataModel;
  CONFIG.Actor.dataModels.npc = NPCDataModel;

  // Item sub-types
  CONFIG.Item.dataModels.weapon = WeaponDataModel;
  CONFIG.Item.dataModels.spell = SpellDataModel;

  // Custom document classes
  CONFIG.Actor.documentClass = MyActor;
  CONFIG.Item.documentClass = MyItem;
});
```

## Data Preparation

Two-phase preparation on document classes:

```javascript
class MyActor extends Actor {
  // Phase 1: Before ActiveEffects applied, before embedded docs prepared
  prepareBaseData() {
    super.prepareBaseData();
    // Set base values
  }

  // Phase 2: After ActiveEffects, after embedded docs
  prepareDerivedData() {
    super.prepareDerivedData();
    const system = this.system;

    // Calculate ability modifiers
    for (const [key, ability] of Object.entries(system.abilities)) {
      ability.mod = Math.floor((ability.value - 10) / 2);
    }

    // Clamp health
    system.resources.health.value = Math.clamped(
      system.resources.health.value, 0, system.resources.health.max
    );

    // Derive level from experience
    system.level = Math.floor(system.experience / 1000) + 1;
  }
}
```

## Data Migration

Handle schema changes across versions:

```javascript
class HeroDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() { /* ... */ }

  static migrateData(source) {
    // Rename old field to new field
    if ("hp" in source) {
      source.resources ??= {};
      source.resources.health = { value: source.hp, max: source.hpMax };
      delete source.hp;
      delete source.hpMax;
    }
    // Convert numeric level to progress
    if (Number.isNumeric(source.level)) {
      source.experience = source.level * 1000;
    }
    return super.migrateData(source);
  }
}
```

## Token Resource Bars

Configure trackable attributes for token bars:

```javascript
Hooks.once("init", () => {
  CONFIG.Actor.trackableAttributes = {
    hero: {
      bar: ["resources.health", "resources.mana"],  // bar attributes (value/max)
      value: ["level"]                                // value-only attributes
    },
    npc: {
      bar: ["resources.health"],
      value: []
    }
  };
});
```

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
