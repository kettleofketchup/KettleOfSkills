---
description: libWrapper, socketlib, Vite build setup, Svelte/TypeScript integration, TyphonJS
last_updated: 2026-03-18
---

# Development Libraries & Tools

## libWrapper

Safe method patching to avoid conflicts between modules. Three wrapper types:

```javascript
// Declare dependency in module.json
// "relationships": { "requires": [{ "id": "lib-wrapper", "type": "module" }] }

Hooks.once("init", () => {
  // WRAPPER - calls original, can modify args/return
  libWrapper.register("my-module", "Actor.prototype.prepareData", function(wrapped, ...args) {
    wrapped(...args);  // Must call original
    this.system.customField = "value";
  }, "WRAPPER");

  // MIXED - calls original conditionally
  libWrapper.register("my-module", "ChatMessage.prototype.getHTML", function(wrapped, ...args) {
    if (someCondition) return customHTML;
    return wrapped(...args);
  }, "MIXED");

  // OVERRIDE - completely replaces (use sparingly)
  libWrapper.register("my-module", "Token.prototype._draw", function() {
    return customDraw();
  }, "OVERRIDE");
});

// Unregister
libWrapper.unregister("my-module", "Actor.prototype.prepareData");
```

Priority: WRAPPER (lowest conflict) > MIXED > OVERRIDE (highest conflict).

## socketlib

Simplified socket communication between clients:

```javascript
let socket;
Hooks.once("socketlib.ready", () => {
  socket = socketlib.registerModule("my-module");
  socket.register("doSomething", doSomething);
  socket.register("gmAction", gmAction);
});

// Call patterns
await socket.executeAsGM("gmAction", arg1, arg2);
await socket.executeAsUser("doSomething", userId, ...);
await socket.executeForEveryone("doSomething", ...);
await socket.executeForAllGMs("gmAction", ...);
```

## Vite Build Setup

```javascript
// vite.config.mjs
import { defineConfig } from "vite";

export default defineConfig({
  root: "src/",
  base: "/modules/my-module/",
  publicDir: false,
  server: {
    port: 30001,
    proxy: {
      "^(?!/modules/my-module/)": "http://localhost:30000/",
      "/socket.io": { target: "ws://localhost:30000", ws: true }
    }
  },
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    sourcemap: true,
    lib: { entry: "main.mjs", formats: ["es"], fileName: "main" }
  }
});
```

Enable in Foundry: set `FOUNDRY_HOT_RELOAD=true` for asset hot-reloading.

## TypeScript

```bash
npm install --save-dev typescript @league-of-foundry-developers/foundry-vtt-types
```

```json
{
  "compilerOptions": {
    "target": "ES2022", "module": "ES2022",
    "moduleResolution": "bundler", "strict": true,
    "types": ["@league-of-foundry-developers/foundry-vtt-types"]
  }
}
```

## Svelte + TyphonJS Runtime Library (TRL)

TRL provides Foundry-aware Svelte components with ApplicationV2 integration:

```bash
npx degit typhonjs-fvtt-demo/template-svelte-esm my-module
cd my-module && npm install
```

## Project Templates

| Template | Stack | URL |
|----------|-------|-----|
| TRL Svelte ESM | Svelte + Vite + TyphonJS | `typhonjs-fvtt-demo/template-svelte-esm` |
| League Module Template | Vanilla + Gulp | `League-of-Foundry-Developers/foundry-module-template` |
| Boilerplate System | Vanilla system starter | `foundryvtt/world-building-system` |

## DevMode & Useful APIs

See `references/modules/libraries-tools.md` for Foundry DevMode debug flags and common UI/dialog/dice APIs.
