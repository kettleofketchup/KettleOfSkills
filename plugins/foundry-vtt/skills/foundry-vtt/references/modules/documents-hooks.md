---
description: Foundry VTT Document model, hooks system, lifecycle events, CRUD hooks, render hooks
last_updated: 2026-03-18
---

# Documents & Hooks

## Core Document Types

| Document | Description | Key Properties |
|----------|-------------|----------------|
| `Actor` | Characters, NPCs, vehicles | system, items, effects, prototypeToken |
| `Item` | Equipment, spells, features | system, effects |
| `Scene` | Maps with tokens, lights, walls | tokens, lights, walls, drawings, notes |
| `JournalEntry` | Notes, handouts (multi-page v10+) | pages[] |
| `ChatMessage` | Chat/dice messages | content, rolls, speaker |
| `Macro` | Executable scripts/chat commands | command, type (script/chat) |
| `RollTable` | Random tables | results[], formula |
| `Playlist` | Audio playlists | sounds[], playing |
| `Cards` | Card decks and hands | cards[], type |
| `User` | Connected players | role, character, color |
| `Combat` | Initiative tracker | combatants[], round, turn |
| `Folder` | Organizes documents | type, sorting |

## Document CRUD

```javascript
// Create
const actor = await Actor.create({ name: "Hero", type: "hero" });

// Read
const actor = game.actors.get("actorId");
const items = game.items.filter(i => i.type === "weapon");

// Update
await actor.update({ "system.resources.health.value": 5 });
await actor.update({ "name": "New Name", "system.level": 10 });

// Delete
await actor.delete();

// Embedded documents (items owned by actor)
await actor.createEmbeddedDocuments("Item", [{ name: "Sword", type: "weapon" }]);
await actor.updateEmbeddedDocuments("Item", [{ _id: "itemId", "system.damage": "2d6" }]);
await actor.deleteEmbeddedDocuments("Item", ["itemId"]);
```

## Hooks System

### Registration

```javascript
Hooks.on("hookName", callback);        // Persistent listener
Hooks.once("hookName", callback);      // Fire once then remove
Hooks.off("hookName", callbackRef);    // Remove listener
Hooks.callAll("customHook", ...args);  // Fire custom hook (all listeners)
Hooks.call("customHook", ...args);     // Fire custom hook (stoppable)
```

### Lifecycle Hooks (fire order)

| Hook | When | Use For |
|------|------|---------|
| `init` | Before any data loaded | Register settings, document classes, sheets |
| `i18nInit` | After localization loaded | Modify translations |
| `setup` | After init, before ready | Data-dependent setup |
| `ready` | Everything loaded, world ready | UI modifications, data queries |

### Document Hooks

Pre-hooks can cancel operations by returning `false`:

```javascript
// Pattern: pre{Operation}{DocumentType}, {operation}{DocumentType}
Hooks.on("preCreateActor", (document, data, options, userId) => {
  // Return false to cancel creation
});
Hooks.on("createActor", (document, options, userId) => {
  // After creation
});
```

| Pre-Hook | Post-Hook | Trigger |
|----------|-----------|---------|
| `preCreateActor` | `createActor` | Actor created |
| `preUpdateActor` | `updateActor` | Actor updated |
| `preDeleteActor` | `deleteActor` | Actor deleted |
| `preCreateItem` | `createItem` | Item created |
| `preUpdateItem` | `updateItem` | Item updated |
| `preDeleteItem` | `deleteItem` | Item deleted |
| `preCreateChatMessage` | `createChatMessage` | Chat message sent |

Same pattern for all document types: Scene, JournalEntry, Macro, RollTable, etc.

### Render Hooks

Fire when Applications render. Follow inheritance chain:

```javascript
// Fires for ALL applications
Hooks.on("renderApplication", (app, html, data) => {});

// Fires for specific sheet type (+ all parent render hooks)
Hooks.on("renderActorSheet", (app, html, data) => {});
Hooks.on("renderItemSheet", (app, html, data) => {});
Hooks.on("renderChatMessage", (message, html, data) => {});

// Close hooks
Hooks.on("closeActorSheet", (app, html) => {});
```

### Other Useful Hooks

| Hook | When |
|------|------|
| `canvasReady` | Canvas fully rendered |
| `updateToken` | Token moved/changed on canvas |
| `controlToken` | Token selected/deselected |
| `hoverToken` | Mouse enters/leaves token |
| `chatMessage` | Before chat message processed |
| `getChatLogEntryContext` | Context menu on chat messages |
| `getActorDirectoryEntryContext` | Context menu on actor sidebar |
| `renderSidebarTab` | Sidebar tab rendered |
| `dropActorSheetData` | Item dropped on actor sheet |
| `hotbarDrop` | Macro dropped on hotbar |
| `targetToken` | Token targeted/untargeted |
| `combatStart` | Combat begins |
| `combatTurn` | Combat turn advances |
| `combatRound` | Combat round advances |

## Global Objects

| Object | Access |
|--------|--------|
| `game.actors` | All world actors |
| `game.items` | All world items |
| `game.scenes` | All scenes |
| `game.users` | All connected users |
| `game.user` | Current user |
| `game.settings` | Settings API |
| `game.socket` | Socket.io instance |
| `game.i18n` | Localization |
| `game.packs` | Compendium collection |
| `canvas` | Active scene canvas |
| `ui.notifications` | Toast notifications |
| `CONFIG` | Global configuration |
