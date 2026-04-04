---
description: CI/CD testing, Jest/Vitest outside Foundry, mocking Foundry API, test scenarios, packaging
last_updated: 2026-03-18
---

# CI/CD Testing & Packaging

## Unit Testing Outside Foundry (Jest/Vitest)

Test pure logic without Foundry runtime. Mock the global API:

### Vitest Setup

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
globalThis.foundry = { utils: { mergeObject: (a, b) => ({ ...a, ...b }), randomID: () => Math.random().toString(36).substring(2) } };
globalThis.ui = { notifications: { info: vi.fn(), warn: vi.fn(), error: vi.fn() } };
```

### Example Unit Test

```javascript
// test/utils.test.mjs
import { describe, it, expect } from "vitest";
import { calculateModifier, clampHealth } from "../src/utils.mjs";

describe("calculateModifier", () => {
  it("returns 0 for score 10", () => {
    expect(calculateModifier(10)).toBe(0);
  });
  it("returns -1 for score 8", () => {
    expect(calculateModifier(8)).toBe(-1);
  });
  it("returns 5 for score 20", () => {
    expect(calculateModifier(20)).toBe(5);
  });
});

describe("clampHealth", () => {
  it("clamps negative to 0", () => {
    expect(clampHealth(-5, 20)).toBe(0);
  });
  it("clamps over max", () => {
    expect(clampHealth(25, 20)).toBe(20);
  });
});
```

## Test Scenarios in Foundry

### Creating Test Worlds

1. Create a dedicated "test" world in Foundry
2. Pre-populate with known actors, items, scenes
3. Use Quench to validate expected state
4. Reset world data between test suites

### Automated Test World Setup

```javascript
// test/fixtures.mjs - create test fixtures
export async function setupTestWorld() {
  // Clean existing test data
  const testActors = game.actors.filter(a => a.name.startsWith("TEST_"));
  for (const a of testActors) await a.delete();

  // Create fixtures
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

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Test Module
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm test            # Vitest unit tests

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx eslint src/
      - run: npx tsc --noEmit    # TypeScript type checking

  build:
    runs-on: ubuntu-latest
    needs: [unit-tests, lint]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: module-dist
          path: dist/
```

## Packaging for Distribution

### Module ZIP Structure

```bash
# Build and package
npm run build
cd dist && zip -r ../my-module.zip . && cd ..
```

ZIP must contain module files at root level (not nested in subdirectory):
```
my-module.zip
├── module.json
├── scripts/
├── styles/
├── templates/
├── lang/
└── packs/
```

### Release Manifest URL

Point `manifest` in module.json to a stable URL (GitHub releases):
```json
{
  "manifest": "https://github.com/user/my-module/releases/latest/download/module.json",
  "download": "https://github.com/user/my-module/releases/latest/download/my-module.zip"
}
```

### Release

Tag a version, CI builds ZIP + uploads to GitHub Releases. Users install via: Setup > Add-on Modules > Install Module > paste manifest URL.
