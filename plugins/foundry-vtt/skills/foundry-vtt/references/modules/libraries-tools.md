---
description: Foundry DevMode debug module, notifications, dialogs, dice rolls, FilePicker APIs
last_updated: 2026-03-18
---

# Foundry DevMode & Useful APIs

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

Declare as a recommended dependency in module.json:
```json
{
  "relationships": {
    "recommends": [{ "id": "_dev-mode", "type": "module" }]
  }
}
```

## Notifications

```javascript
ui.notifications.info("Saved successfully");
ui.notifications.warn("Low health!");
ui.notifications.error("Failed to load");

// Permanent notification (stays until dismissed)
const id = ui.notifications.info("Processing...", { permanent: true });
ui.notifications.remove(id);
```

## Dialogs (ApplicationV2)

```javascript
// Confirm dialog
const confirmed = await foundry.applications.api.DialogV2.confirm({
  content: "Are you sure?",
  rejectClose: false   // resolve false instead of rejecting on close
});

// Prompt for input
const value = await foundry.applications.api.DialogV2.prompt({
  content: '<input type="text" name="value" placeholder="Enter value"/>',
  ok: { callback: (event, button, dialog) => button.form.elements.value.value }
});

// Custom buttons
const result = await foundry.applications.api.DialogV2.wait({
  content: "Choose an option",
  buttons: [
    { label: "Option A", action: "a" },
    { label: "Option B", action: "b" }
  ]
});
```

## Dice Rolls

```javascript
// Basic roll
const roll = new Roll("2d6 + @mod", { mod: 3 });
await roll.evaluate();
console.log(roll.total);  // e.g. 11

// Post to chat
await roll.toMessage({
  speaker: ChatMessage.getSpeaker(),
  flavor: "Attack Roll"
});

// Roll table
const table = game.tables.getName("Random Encounter");
const result = await table.roll();

// DSN (Dice So Nice) integration
if (game.modules.get("dice-so-nice")?.active) {
  await game.dice3d.showForRoll(roll);
}
```

## FilePicker

```javascript
// Open picker for user to select a file
const result = await FilePicker.browse("data", "");
// result.files - array of file paths
// result.dirs - array of directory paths

// Open picker as dialog
const picker = new FilePicker({
  type: "image",       // "image", "audio", "video", "font", "imagevideo", "folder", "any"
  current: "modules/my-module/assets/",
  callback: (path) => { /* handle selected path */ }
});
picker.render(true);
```

## Canvas & Tokens

```javascript
// Access canvas layers
canvas.tokens.placeables       // All token objects
canvas.drawings.placeables     // All drawing objects

// Selected tokens
canvas.tokens.controlled       // Array of controlled tokens

// Token actor
const token = canvas.tokens.controlled[0];
token.actor.update({ "system.hp.value": 10 });

// Ping a location
canvas.ping({ x: 500, y: 500 });
```
