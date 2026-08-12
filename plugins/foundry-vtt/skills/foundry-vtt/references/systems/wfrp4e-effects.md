---
description: WFRP4e Active Effects triggers system, script examples, world scripts, development setup, community modules
last_updated: 2026-03-20
---

# WFRP4e Effects, Triggers & Development

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

// preRollTest: Add SL bonus
args.test.preData.slBonus += 2
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

### foundryconfig.json

```json
{
  "dataPath": "/home/user/.local/share/FoundryVTT",
  "symlink": true
}
```

Running `npm run build` compiles SCSS + bundles JS. `npm run pack` compiles compendium packs.

## Career Replacements

```javascript
game.wfrp4e.utility.mergeCareerReplacements({
  wolfkin: { "Flagellant": ["Hunter"] }
});
```

Replaces career availability for species in chargen.

## Community Modules

| Module | Purpose |
|--------|---------|
| `wfrp4e-gm-toolkit` | GM tools: random tables, encounter generators |
| `foundryvtt-forien-armoury` | Extra equipment and gear |
| `wfrp4e-npc-generator` | NPC generation from career tables |
| `wfrp4e-core` | Official Cubicle 7 premium content pack |
