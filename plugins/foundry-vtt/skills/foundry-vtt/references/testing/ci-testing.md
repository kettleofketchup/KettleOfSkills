---
description: Unit testing outside Foundry with Vitest, mocking Foundry API globals, test scenarios, fixtures
last_updated: 2026-03-18
---

# CI/CD Testing

## Unit Testing Outside Foundry (Vitest)

Test pure logic without Foundry runtime. Mock the global API:

```bash
npm install --save-dev vitest
```

```javascript
// vitest.config.mjs
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.mjs"]
  }
});
```

### Mocking Foundry Globals

```javascript
// test/setup.mjs - minimal Foundry API mock
globalThis.game = {
  settings: {
    get: vi.fn(),
    set: vi.fn(),
    register: vi.fn()
  },
  i18n: { localize: vi.fn((key) => key) },
  actors: { get: vi.fn(), filter: vi.fn(() => []) },
  user: { isGM: true, id: "mockUserId" },
  modules: new Map()
};

globalThis.CONFIG = { Actor: {}, Item: {} };
globalThis.Hooks = {
  on: vi.fn(), once: vi.fn(), off: vi.fn(),
  callAll: vi.fn(), call: vi.fn()
};
globalThis.foundry = {
  utils: {
    mergeObject: (a, b) => ({ ...a, ...b }),
    randomID: () => Math.random().toString(36).substring(2)
  }
};
globalThis.ui = { notifications: { info: vi.fn(), warn: vi.fn(), error: vi.fn() } };
```

### Example Unit Test

```javascript
// test/utils.test.mjs
import { describe, it, expect } from "vitest";
import { calculateModifier, clampHealth } from "../src/utils.mjs";

describe("calculateModifier", () => {
  it("returns 0 for score 10", () => expect(calculateModifier(10)).toBe(0));
  it("returns -1 for score 8", () => expect(calculateModifier(8)).toBe(-1));
  it("returns 5 for score 20", () => expect(calculateModifier(20)).toBe(5));
});
```

## Test Scenarios in Foundry

### Creating Test Worlds

1. Create a dedicated "test" world in Foundry
2. Pre-populate with known actors, items, scenes
3. Use Quench to validate expected state
4. Reset world data between test suites

### Automated Test Fixtures

```javascript
// test/fixtures.mjs
export async function setupTestWorld() {
  const testActors = game.actors.filter(a => a.name.startsWith("TEST_"));
  for (const a of testActors) await a.delete();

  const hero = await Actor.create({
    name: "TEST_Hero", type: "hero",
    system: { level: 5, resources: { health: { value: 30, max: 30 } } }
  });
  const weapon = await Item.create({
    name: "TEST_Sword", type: "weapon",
    system: { damage: "2d6", weight: 3 }
  });
  await hero.createEmbeddedDocuments("Item", [weapon.toObject()]);
  return { hero, weapon };
}

export async function teardownTestWorld({ hero, weapon }) {
  await hero?.delete();
  await weapon?.delete();
}
```

## CI Pipeline & Packaging

See `references/testing/ci-testing-pipeline.md` for GitHub Actions workflows and module distribution packaging.
