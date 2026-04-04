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
    // Add custom logic after
    this.system.customField = "value";
  }, "WRAPPER");

  // MIXED - calls original conditionally
  libWrapper.register("my-module", "ChatMessage.prototype.getHTML", function(wrapped, ...args) {
    if (someCondition) return customHTML;
    return wrapped(...args);  // Call original only sometimes
  }, "MIXED");

  // OVERRIDE - completely replaces (use sparingly)
  libWrapper.register("my-module", "Token.prototype._draw", function() {
    // Original never called
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
// "relationships": { "requires": [{ "id": "socketlib", "type": "module" }] }

let socket;
Hooks.once("socketlib.ready", () => {
  socket = socketlib.registerModule("my-module");

  // Register callable functions
  socket.register("doSomething", doSomething);
  socket.register("gmAction", gmAction);
});

async function doSomething(actorId, damage) {
  const actor = game.actors.get(actorId);
  await actor.update({ "system.hp.value": actor.system.hp.value - damage });
}

// Call patterns
await socket.executeAsGM("gmAction", arg1, arg2);      // Only GM executes
await socket.executeAsUser("doSomething", userId, ...);  // Specific user
await socket.executeForEveryone("doSomething", ...);     // All clients
await socket.executeForOtherGMs("gmAction", ...);        // All other GMs
await socket.executeForAllGMs("gmAction", ...);          // All GMs
```

## Vite Build Setup

Vite dev server sits in front of Foundry, intercepting module requests for HMR:

```javascript
// vite.config.mjs
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";  // optional

export default defineConfig({
  root: "src/",
  base: "/modules/my-module/",
  publicDir: false,
  server: {
    port: 30001,
    open: false,
    proxy: {
      // Proxy everything except module files to Foundry
      "^(?!/modules/my-module/)": "http://localhost:30000/",
      "/socket.io": { target: "ws://localhost:30000", ws: true }
    }
  },
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    sourcemap: true,
    lib: {
      entry: "main.mjs",
      formats: ["es"],
      fileName: "main"
    }
  }
});
```

Enable in Foundry: set `FOUNDRY_HOT_RELOAD=true` for asset hot-reloading.

## TypeScript

```bash
npm install --save-dev typescript @league-of-foundry-developers/foundry-vtt-types
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "types": ["@league-of-foundry-developers/foundry-vtt-types"]
  },
  "include": ["src/**/*.ts"]
}
```

## Svelte + TyphonJS Runtime Library (TRL)

TRL provides Foundry-aware Svelte components with ApplicationV2 integration:

```bash
# Use the TRL template
npx degit typhonjs-fvtt-demo/template-svelte-esm my-module
cd my-module && npm install
```

Svelte components replace Handlebars templates for reactive UIs. HMR preserves component state during development.

## Project Templates

| Template | Stack | URL |
|----------|-------|-----|
| TRL Svelte ESM | Svelte + Vite + TyphonJS | `typhonjs-fvtt-demo/template-svelte-esm` |
| League Module Template | Vanilla + Gulp | `League-of-Foundry-Developers/foundry-module-template` |
| Boilerplate System | Vanilla system starter | `foundryvtt/world-building-system` |

## Foundry DevMode Module

Developer tools by League of Foundry Developers:

```javascript
// Register debug flag
Hooks.once("devModeReady", ({ registerPackageDebugFlag }) => {
  registerPackageDebugFlag("my-module");
});

// Conditional debug logging
if (game.modules.get("_dev-mode")?.api?.getPackageDebugValue("my-module")) {
  console.log("Debug:", data);
}
```

## Useful APIs

```javascript
// Notifications
ui.notifications.info("Saved successfully");
ui.notifications.warn("Low health!");
ui.notifications.error("Failed to load");

// Dialogs
const confirmed = await foundry.applications.api.DialogV2.confirm({
  content: "Are you sure?",
  rejectClose: false
});

// Roll dice
const roll = new Roll("2d6 + @mod", { mod: 3 });
await roll.evaluate();
await roll.toMessage({ speaker: ChatMessage.getSpeaker() });

// FilePicker
const path = await new FilePicker({ type: "image" }).browse();
```
