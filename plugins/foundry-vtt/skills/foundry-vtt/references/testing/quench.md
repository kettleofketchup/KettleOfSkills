---
description: Quench in-Foundry test runner, Mocha/Chai/fast-check, test batch API, snapshot testing
last_updated: 2026-03-18
---

# Quench Testing Framework

In-Foundry test runner powered by Mocha + Chai + fast-check. Runs tests inside a live Foundry instance with full API access.

## Setup

Install Quench module in Foundry. Declare optional dependency in module.json:

```json
{
  "relationships": {
    "recommends": [{ "id": "quench", "type": "module" }]
  }
}
```

## Registering Test Batches

```javascript
Hooks.on("quenchReady", (quench) => {
  quench.registerBatch(
    "my-module.core.actors",                    // unique key
    (context) => {
      const { describe, it, assert, expect } = context;

      describe("Actor Creation", function() {
        let testActor;

        before(async function() {
          testActor = await Actor.create({
            name: "Test Hero", type: "hero"
          });
        });

        after(async function() {
          await testActor?.delete();
        });

        it("should create actor with correct name", function() {
          assert.equal(testActor.name, "Test Hero");
        });

        it("should have default health", function() {
          expect(testActor.system.resources.health.value).to.equal(10);
        });

        it("should derive ability modifiers", function() {
          expect(testActor.system.abilities.str.mod).to.be.a("number");
        });
      });
    },
    { displayName: "MYMOD: Actor Tests" }       // shown in Quench UI
  );
});
```

## Context Object

The `context` parameter provides:

| Property | Source | Description |
|----------|--------|-------------|
| `describe`, `it`, `before`, `beforeEach`, `after`, `afterEach` | Mocha | Test structure |
| `assert` | Chai | Assert-style assertions |
| `expect` | Chai | Expect-style assertions |
| `should` | Chai | Should-style assertions |
| `fc` | fast-check | Property-based testing |
| `utils` | Mocha | Mocha utilities |

## Test Patterns

### Document CRUD Testing

```javascript
describe("Item Management", function() {
  it("should add item to actor", async function() {
    const actor = await Actor.create({ name: "Test", type: "hero" });
    const [item] = await actor.createEmbeddedDocuments("Item", [
      { name: "Sword", type: "weapon", "system.damage": "2d6" }
    ]);
    expect(actor.items.size).to.equal(1);
    expect(item.name).to.equal("Sword");
    await actor.delete();
  });
});
```

### Hook Testing

```javascript
describe("Custom Hooks", function() {
  it("should fire preCreateActor hook", async function() {
    let hookFired = false;
    const hookId = Hooks.on("preCreateActor", () => { hookFired = true; });
    await Actor.create({ name: "Hook Test", type: "hero" });
    expect(hookFired).to.be.true;
    Hooks.off("preCreateActor", hookId);
  });
});
```

### Roll Testing

```javascript
describe("Dice Rolls", function() {
  it("should evaluate 2d6 roll", async function() {
    const roll = new Roll("2d6 + 3");
    await roll.evaluate();
    expect(roll.total).to.be.at.least(5).and.at.most(15);
  });
});
```

### Property-Based Testing (fast-check)

```javascript
describe("Data Validation", function() {
  it("should clamp health between 0 and max", function() {
    const { fc } = context;
    fc.assert(fc.property(
      fc.integer({ min: -100, max: 200 }),
      (value) => {
        const clamped = Math.clamped(value, 0, 100);
        return clamped >= 0 && clamped <= 100;
      }
    ));
  });
});
```

## Snapshot Testing

```javascript
it("should match actor data snapshot", function() {
  const data = { name: testActor.name, type: testActor.type };
  assert.matchSnapshot(data);
  // or: expect(data).to.matchSnapshot();
});
```

Snapshots stored in `Data/__snapshots__/<package>/`. Update via Quench UI button on failure.

## Running Tests

### Via Quench UI
Open Quench application in Foundry. Select batches, click Run.

### Via API (headless/CI)
```javascript
// Run all batches
await quench.runBatches("**");

// Run specific batches with JSON report
const report = await quench.runBatches(
  ["my-module.core.actors"],
  { json: true }
);
```

### Report Hook
```javascript
Hooks.on("quenchReports", (reports) => {
  console.log("Test results:", reports.json);
});
```

## Batch Key Conventions

- Format: `<package-id>.<category>.<description>`
- Examples: `my-module.core.actors`, `my-module.sheets.rendering`, `my-module.integration.combat`
- Display name: `MYMOD: Actor Tests`, `MYMOD: Sheet Rendering`

## TypeScript Support

```bash
npm install --save-dev @ethaks/fvtt-quench
```

```json
// tsconfig.json
{ "compilerOptions": { "types": ["@ethaks/fvtt-quench"] } }
```
