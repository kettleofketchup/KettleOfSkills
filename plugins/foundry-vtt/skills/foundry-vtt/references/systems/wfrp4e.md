---
description: Warhammer Fantasy Roleplay 4e (wfrp4e) system for Foundry VTT, game.wfrp4e API, actor/item types, effects triggers, custom species, world scripts, module development, config extension
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
| `ammunition` | Arrow/bolt/shot types |
| `trapping` | Generic equipment/gear with encumbrance |
| `container` | Bags/backpacks that hold other items |
| `skill` | Skills (basic/advanced) with advances |
| `talent` | Talents with tests, max advances |
| `spell` | Spells with CN, range, duration, lore |
| `prayer` | Religious prayers with range, duration |
| `trait` | Creature/species traits |
| `career` | Career with level, characteristics, skills, talents |
| `injury` | Critical injuries |
| `disease` | Diseases with symptoms, duration, contraction |
| `mutation` | Chaos mutations |
| `psychology` | Psychological conditions |
| `money` | Coins (gold crowns, silver shillings, brass pennies) |

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
game.wfrp4e.config.availability         // Item availability levels
game.wfrp4e.config.difficultyModifiers  // Test difficulty modifiers
game.wfrp4e.config.difficultyLabels     // Difficulty display names
game.wfrp4e.config.xpCost              // Advancement cost tables
game.wfrp4e.config.weaponQualities     // Weapon quality definitions
game.wfrp4e.config.weaponFlaws         // Weapon flaw definitions
```

## Extending Config (World Scripts / Modules)

Use `Hooks.once("init")` + `foundry.utils.mergeObject()`:

```javascript
Hooks.once("init", () => {
  // Add custom item availability
  foundry.utils.mergeObject(game.wfrp4e.config.availability, {
    legendary: "Legendary", unique: "Unique"
  });

  // Add custom difficulty modifiers
  foundry.utils.mergeObject(game.wfrp4e.config, {
    difficultyModifiers: { godly: 100, ungodly: -100 },
    difficultyLabels: { godly: "Godly (+100)", ungodly: "Ungodly (-100)" }
  });
});
```

## Adding Custom Species

16 config fields define a species. All accessed via `game.wfrp4e.config`:

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
  c.speciesTalents.wolfkin = ["Night Vision", "Lightning Reflexes, Warrior Born"]; // comma = choice
  c.speciesRandomTalents.wolfkin = { talents: 2 }; // 2 random from default table
  c.speciesTraits.wolfkin = ["Arboreal"];
  c.speciesMovement.wolfkin = 5;
  c.speciesFate.wolfkin = 1;
  c.speciesRes.wolfkin = 2;
  c.speciesExtra.wolfkin = 2;  // Extra fate/resilience points to distribute
  c.speciesAge.wolfkin = "10+5d10";
  c.speciesHeight.wolfkin = { die: "1d10", feet: 5, inches: 2 };

  c.extraSpecies.push("wolfkin"); // Available in chargen but not rollable
});
```

### Subspecies

Inherit from parent; only override what differs:

```javascript
c.subspecies.wolfkin = {};
c.subspecies.wolfkin.arctic = {
  name: "Arctic Wolfkin",
  talents: ["Coolheaded", "Very Resilient, Hardy"],
  movement: 4
};
```

Career replacements: `game.wfrp4e.utility.mergeCareerReplacements({ wolfkin: { "Flagellant": ["Hunter"] } })`

## Effects & Triggers System

WFRP4e has 60+ script triggers on Active Effects. Key categories:

### Lifecycle Triggers

| Trigger | When | args |
|---------|------|------|
| `prepareData` | After base data calculated (wounds, encumbrance) | `args.actor`, `args.item` |
| `prePrepareData` | Before base data calculation | `args.actor` |
| `preUpdateActor` | Before actor update | `args.actor`, `args.data` |
| `createActor` | After actor creation | `args.actor` |

### Combat Triggers

| Trigger | When | args |
|---------|------|------|
| `preRollTest` | Before any test roll | `args.test` |
| `rollTest` | After test resolved | `args.test` |
| `preRollWeaponTest` | Before weapon test | `args.test`, `args.weapon` |
| `rollWeaponTest` | After weapon test resolved | `args.test` |
| `preRollCastingTest` | Before casting test | `args.test`, `args.spell` |
| `preOpposedAttacker` | Before opposed (attacker) | `args.opposedTest` |
| `preOpposedDefender` | Before opposed (defender) | `args.opposedTest` |
| `calculateOpposedDamage` | Damage calculation | `args.damage`, `args.opposedTest` |
| `preApplyDamage` | Before damage applied | `args.actor`, `args.damage` |
| `applyDamage` | After damage applied | `args.actor`, `args.totalWoundLoss` |

### Condition Triggers

| Trigger | When |
|---------|------|
| `preApplyCondition` | Before condition applied |
| `applyCondition` | After condition applied |

### Example Effect Scripts

```javascript
// prepareData: Add movement speed
args.actor.system.details.move.run += 4

// prepareData: Add armor points
this.actor.system.status.addArmour(2, { source: this.effect })

// prepareData: Set ward save
this.actor.system.status.ward.value = 9

// rollWeaponTest: Add extra damage on crit
if (args.test.result.critical) args.test.result.damage += 5
```

## World Scripts Setup

Add to `world.json`:
```json
{ "esmodules": ["my-script.mjs"] }
```

Create `my-script.mjs` in world folder. Restart Foundry after manifest changes.

For reusable code, prefer a module (module.json + esmodules) over world scripts.

## Development Setup

```bash
git clone https://github.com/moo-man/WFRP4e-FoundryVTT && cd WFRP4e-FoundryVTT
npm install && cp example.foundryconfig.json foundryconfig.json
# Edit foundryconfig.json: set "path" to Foundry data dir, then:
npm run build && npm run pack
```

## Community Modules

Key modules: `wfrp4e-gm-toolkit` (GM tools), `foundryvtt-forien-armoury` (extra gear), `wfrp4e-npc-generator` (NPC gen), `wfrp4e-core` (official Cubicle 7 premium content).
