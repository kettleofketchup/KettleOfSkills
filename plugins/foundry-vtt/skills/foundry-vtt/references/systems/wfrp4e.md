---
description: Warhammer Fantasy Roleplay 4e (wfrp4e) system, game.wfrp4e API, actor/item types, custom species, config extension
last_updated: 2026-03-20
---

# WFRP4e System (Warhammer Fantasy Roleplay 4e)

System by moo-man, officially approved by Cubicle 7. Repo: `moo-man/WFRP4e-FoundryVTT`.
Current: v9.0 (Foundry V13 compatible, AppV2). Built with Rollup, SCSS, Handlebars.

## Actor Types

| Type | Description |
|------|-------------|
| `character` | Player characters with full career progression, experience, fate/resilience/fortune/resolve |
| `npc` | NPCs/creatures with simplified sheets, career-based stat generation |
| `vehicle` | Vehicles (ships, carts) with crew, passengers, cargo |

## Item Types

| Type | Description |
|------|-------------|
| `weapon` | Melee/ranged weapons with damage, qualities, flaws |
| `armour` | Armor pieces with AP per location (head, body, arms, legs) |
| `skill` | Skills (basic/advanced) with advances |
| `talent` | Talents with tests, max advances |
| `spell` | Spells with CN, range, duration, lore |
| `prayer` | Religious prayers with range, duration |
| `trait` | Creature/species traits |
| `career` | Career with level, characteristics, skills, talents |
| `trapping` | Generic equipment/gear with encumbrance |
| `injury` / `disease` / `mutation` / `psychology` / `money` | Status/condition item types |

## game.wfrp4e API

Available after `init` hook:

```javascript
game.wfrp4e.config          // All system configuration (species, careers, skills, etc.)
game.wfrp4e.utility         // Utility methods
game.wfrp4e.tables          // Table lookup methods
game.wfrp4e.opposedHandler  // Opposed test resolution
```

### Key Config Objects

```javascript
game.wfrp4e.config.species              // { human: "Human", dwarf: "Dwarf", ... }
game.wfrp4e.config.speciesCharacteristics  // { human: { ws: "2d10+20", ... } }
game.wfrp4e.config.speciesSkills        // { human: ["Animal Care", ...] }
game.wfrp4e.config.speciesTalents       // { human: ["Doomed", "Savvy, Suave"] }
game.wfrp4e.config.difficultyModifiers  // Test difficulty modifiers
game.wfrp4e.config.difficultyLabels     // Difficulty display names
game.wfrp4e.config.weaponQualities      // Weapon quality definitions
```

## Extending Config

Use `Hooks.once("init")` + `foundry.utils.mergeObject()`:

```javascript
Hooks.once("init", () => {
  foundry.utils.mergeObject(game.wfrp4e.config.availability, {
    legendary: "Legendary", unique: "Unique"
  });
  foundry.utils.mergeObject(game.wfrp4e.config, {
    difficultyModifiers: { godly: 100, ungodly: -100 },
    difficultyLabels: { godly: "Godly (+100)", ungodly: "Ungodly (-100)" }
  });
});
```

## Adding Custom Species

```javascript
Hooks.once("init", () => {
  const c = game.wfrp4e.config;
  c.species.wolfkin = "Wolfkin";
  c.speciesCharacteristics.wolfkin = {
    ws: "2d10+20", bs: "2d10+20", s: "2d10+25", t: "2d10+25",
    i: "2d10+20", ag: "2d10+20", dex: "2d10+15", int: "2d10+15",
    wp: "2d10+20", fel: "2d10+10"
  };
  c.speciesSkills.wolfkin = ["Athletics", "Endurance", "Perception", "Stealth (Rural)"];
  c.speciesTalents.wolfkin = ["Night Vision", "Lightning Reflexes, Warrior Born"];
  c.speciesMovement.wolfkin = 5;
  c.speciesFate.wolfkin = 1;
  c.speciesRes.wolfkin = 2;
  c.speciesAge.wolfkin = "10+5d10";
  c.extraSpecies.push("wolfkin");
});
```

Subspecies inherit from parent (only override what differs):

```javascript
c.subspecies.wolfkin = {};
c.subspecies.wolfkin.arctic = {
  name: "Arctic Wolfkin",
  talents: ["Coolheaded", "Very Resilient, Hardy"],
  movement: 4
};
```

## Effects, World Scripts & Dev Setup

See `references/systems/wfrp4e-effects.md` for the full Effects/Triggers system, world scripts setup, and development build instructions.
