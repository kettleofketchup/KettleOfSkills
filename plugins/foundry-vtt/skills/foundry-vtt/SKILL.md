---
name: foundry-vtt
description: "Foundry VTT virtual tabletop. This skill should be used when developing modules/systems (ApplicationV2, hooks, DataModels, Handlebars), deploying via Docker/Helm with Traefik, or working with WFRP4e."
last_updated: 2026-03-20
---

# Foundry VTT

Virtual tabletop platform for TTRPGs. Node.js server, WebSocket-based, extensible via modules and game systems. Current version: v13.

## Key Concepts

- **Module**: Extends/modifies Foundry functionality (like a plugin)
- **System**: Defines game rules, data schemas, sheets (e.g., dnd5e, pf2e)
- **Document**: Core data type (Actor, Item, Scene, JournalEntry, ChatMessage, Macro, RollTable, Playlist, Cards)
- **Application**: UI window class (legacy Application v1, modern ApplicationV2)
- **Hook**: Event system for lifecycle/render/document events

## Module Quick Start

```
mymodule/
├── module.json          # Package manifest (required)
├── scripts/
│   └── main.mjs         # Entry point (esmodules)
├── templates/            # Handlebars .hbs files
├── styles/               # CSS files
├── packs/                # Compendium data
└── lang/
    └── en.json           # Localization
```

Minimal `module.json`:
```json
{
  "id": "my-module",
  "title": "My Module",
  "version": "1.0.0",
  "compatibility": { "minimum": 12, "verified": "13" },
  "esmodules": ["scripts/main.mjs"],
  "styles": ["styles/module.css"]
}
```

Entry point pattern:
```javascript
Hooks.once("init", () => {
  console.log("Module initializing");
  game.settings.register("my-module", "mySetting", {
    name: "My Setting",
    scope: "world",     // "world" or "client"
    config: true,       // show in settings UI
    type: Boolean,
    default: false
  });
});
Hooks.once("ready", () => {
  console.log("Module ready");
});
```

## Bundled Frameworks

| Library | Purpose |
|---------|---------|
| Handlebars | HTML templating for Application UIs |
| PixiJS | Canvas rendering (lighting, tokens, drawings) |
| jQuery | DOM manipulation (legacy, being phased out) |
| GreenSock (GSAP) | SVG/WebGL animation |
| ProseMirror | Rich text editing (v12+) |

## Top Dev Frameworks/Libraries

| Tool | Purpose |
|------|---------|
| **Vite** | Build tool with HMR, serves dev builds through Foundry |
| **TypeScript** + `@league-of-foundry-developers/foundry-vtt-types` | Type safety |
| **Svelte** + TyphonJS Runtime Library (TRL) | Reactive UI components |
| **libWrapper** | Safe method patching without conflicts |
| **socketlib** | Simplified socket communication abstraction |
| **Quench** | In-Foundry test runner (Mocha + Chai + fast-check) |
| **Foundry DevMode** | Developer tools module by League of Foundry Developers |
| **Rollup/Webpack** | Alternative bundlers |

## Reference Files

| File | Content |
|------|---------|
| `references/modules/manifest.md` | module.json and system.json manifest fields, package structure |
| `references/modules/documents-hooks.md` | Document model, hooks system, lifecycle events |
| `references/modules/sheets-templates.md` | ActorSheet/ItemSheet, ApplicationV2, Handlebars templates |
| `references/modules/data-models.md` | TypeDataModel schemas, field types, migration |
| `references/modules/libraries.md` | libWrapper, socketlib, Vite setup, Svelte/TS integration |
| `references/deployment/k3s.md` | K3s/Kubernetes deployment, Helm charts, PVC, ingress |
| `references/deployment/docker.md` | felddy/foundryvtt-docker env vars, compose, configuration |
| `references/testing/quench.md` | Quench test framework, test batches, Mocha/Chai patterns |
| `references/testing/ci-testing.md` | CI/CD, Jest/Vitest outside Foundry, test scenarios |
| `references/systems/wfrp4e.md` | WFRP4e system: game.wfrp4e API, actor/item types, effects triggers, custom species, world scripts |

## Cross-References

- **K3s cluster**: Use `k3s` skill for cluster setup before deploying Foundry
- **Ingress**: Use `traefik` skill for IngressRoute with WebSocket middleware
- **Storage**: Use `rook-ceph` skill for persistent storage backing Foundry data
- **GitOps**: Use `argocd` skill for deploying Foundry via ApplicationSets
- **Helm**: Use `helm` skill for chart customization and values management
