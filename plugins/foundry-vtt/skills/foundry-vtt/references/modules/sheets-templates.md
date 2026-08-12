---
description: ActorSheet, ItemSheet, ApplicationV2, HandlebarsApplicationMixin, Handlebars templates, partials
last_updated: 2026-03-18
---

# Sheets & Templates

## ApplicationV2 (v12+ preferred)

Modern application framework. Use `HandlebarsApplicationMixin` for template rendering:

```javascript
const { HandlebarsApplicationMixin } = foundry.applications.api;
const { ActorSheetV2 } = foundry.applications.sheets;

class MyActorSheet extends HandlebarsApplicationMixin(ActorSheetV2) {
  static DEFAULT_OPTIONS = {
    classes: ["my-system", "actor-sheet"],
    position: { width: 600, height: 400 },
    actions: {
      rollAbility: MyActorSheet.#onRollAbility,
      editItem: MyActorSheet.#onEditItem
    },
    form: { submitOnChange: true }
  };

  static PARTS = {
    header: { template: "systems/my-system/templates/actor-header.hbs" },
    tabs: { template: "systems/my-system/templates/actor-tabs.hbs" },
    attributes: { template: "systems/my-system/templates/actor-attributes.hbs" },
    inventory: { template: "systems/my-system/templates/actor-inventory.hbs" }
  };

  async _prepareContext(options) {
    const context = await super._prepareContext(options);
    context.system = this.document.system;
    context.items = this.document.items.contents;
    context.isEditable = this.isEditable;
    return context;
  }

  static #onRollAbility(event, target) {
    const ability = target.dataset.ability;
    this.document.rollAbility(ability);
  }

  static #onEditItem(event, target) {
    const itemId = target.closest("[data-item-id]").dataset.itemId;
    this.document.items.get(itemId)?.sheet.render(true);
  }
}
```

### Register Sheet

```javascript
Hooks.once("init", () => {
  Actors.registerSheet("my-system", MyActorSheet, {
    types: ["hero"],
    makeDefault: true,
    label: "MYSYS.SheetHero"
  });
  Items.registerSheet("my-system", MyItemSheet, {
    types: ["weapon", "spell"],
    makeDefault: true
  });
});
```

## v12 vs v13 Migration Notes

| v12 (Legacy) | v13 (Modern) |
|--------------|--------------|
| `Application` base class | `ApplicationV2` base class |
| `getData()` | `_prepareContext()` (async) |
| `activateListeners(html)` + jQuery | `static ACTIONS` + `data-action` attributes |
| `html.find(".btn").click(fn)` | DOM addEventListener or actions system |
| `{{editor}}` helper | `<prose-mirror>` element |
| Single template | Multi-part `PARTS` templates |
| `defaultOptions` static getter | `DEFAULT_OPTIONS` static property |

## Legacy v1 & Handlebars Templates

See `references/modules/sheets-templates-handlebars.md` for legacy Application v1 patterns and Handlebars syntax reference.
