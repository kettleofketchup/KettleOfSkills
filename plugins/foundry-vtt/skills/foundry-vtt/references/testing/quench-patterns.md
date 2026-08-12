---
description: Quench snapshot testing, running tests via UI and API, batch key conventions, TypeScript support
last_updated: 2026-03-18
---

# Quench: Advanced Patterns

## Snapshot Testing

```javascript
it("should match actor data snapshot", function() {
  const data = { name: testActor.name, type: testActor.type };
  assert.matchSnapshot(data);
  // or: expect(data).to.matchSnapshot();
});
```

Snapshots stored in `Data/__snapshots__/<package>/`. Update via Quench UI button on failure.

### Snapshot with Complex Data

```javascript
it("should match item system data", function() {
  const weapon = testActor.items.getName("Sword");
  assert.matchSnapshot({
    damage: weapon.system.damage,
    qualities: weapon.system.qualities
  });
});
```

## Running Tests

### Via Quench UI

Open Quench application in Foundry. Select batches, click Run. Results show pass/fail/pending with Mocha-style output.

### Via API (headless/CI)

```javascript
// Run all batches
await quench.runBatches("**");

// Run specific batches
const report = await quench.runBatches(
  ["my-module.core.actors"],
  { json: true }
);
console.log(report.stats); // { passes, failures, pending, duration }
```

### Report Hook

```javascript
Hooks.on("quenchReports", (reports) => {
  console.log("Test results:", reports.json);
  // Exit process on failure (for CI)
  if (reports.json.stats.failures > 0) process.exit(1);
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

Provides typed `quench` global, `QuenchBatchContext`, `QuenchRunResults`.

## Async Test Patterns

```javascript
describe("Async Operations", function() {
  this.timeout(5000);  // Increase timeout for slow operations

  it("should update actor via socket", async function() {
    const original = testActor.system.resources.health.value;
    await testActor.update({ "system.resources.health.value": original - 5 });
    expect(testActor.system.resources.health.value).to.equal(original - 5);
  });
});
```

## Roll Testing with Quench

```javascript
describe("Dice Rolls", function() {
  it("should evaluate 2d6 roll", async function() {
    const roll = new Roll("2d6 + 3");
    await roll.evaluate();
    expect(roll.total).to.be.at.least(5).and.at.most(15);
  });

  it("should post to chat", async function() {
    const roll = new Roll("1d20");
    await roll.evaluate();
    const msg = await roll.toMessage({}, { create: true });
    expect(msg).to.be.instanceOf(ChatMessage);
    await msg.delete();
  });
});
```
