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

  // Prepare data for templates
  async _prepareContext(options) {
    const context = await super._prepareContext(options);
    context.system = this.document.system;
    context.items = this.document.items.contents;
    context.isEditable = this.isEditable;
    return context;
  }

  // DOM event listeners (v13 style - NOT jQuery)
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

## Legacy Application v1 (pre-v12)

```javascript
class MyActorSheet extends ActorSheet {
  static get defaultOptions() {
    return foundry.utils.mergeObject(super.defaultOptions, {
      classes: ["my-system", "sheet", "actor"],
      template: "systems/my-system/templates/actor-sheet.hbs",
      width: 600, height: 400,
      tabs: [{ navSelector: ".tabs", contentSelector: ".sheet-body" }]
    });
  }

  getData() {
    const context = super.getData();
    context.system = this.actor.system;
    return context;
  }

  activateListeners(html) {
    super.activateListeners(html);
    html.find(".roll-ability").click(this._onRollAbility.bind(this));
  }
}
```

## Handlebars Templates

### Basic Syntax

```handlebars
<h1>{{actor.name}}</h1>
<p>Level: {{system.level}}</p>

{{!-- Conditionals --}}
{{#if isEditable}}
  <input type="text" name="name" value="{{actor.name}}"/>
{{else}}
  <span>{{actor.name}}</span>
{{/if}}

{{!-- Loops --}}
{{#each items as |item|}}
  <li data-item-id="{{item._id}}">
    <img src="{{item.img}}" width="24"/>
    <span>{{item.name}}</span>
    <span>{{item.system.damage}}</span>
  </li>
{{/each}}
```

### Foundry Helpers

```handlebars
{{!-- Localization --}}
<label>{{localize "MYSYS.Strength"}}</label>

{{!-- Number input with data binding --}}
<input type="number" name="system.abilities.str.value"
       value="{{system.abilities.str.value}}" data-dtype="Number"/>

{{!-- Select dropdown --}}
<select name="system.alignment">
  {{selectOptions alignments selected=system.alignment localize=true}}
</select>

{{!-- Rich text editor (v12 legacy) --}}
{{editor content=system.biography target="system.biography" button=true editable=editable}}

{{!-- Rich text editor (v13 ProseMirror) --}}
{{#if editable}}
  <prose-mirror name="system.biography" toggled>{{system.biography}}</prose-mirror>
{{else}}
  {{{system.biography}}}
{{/if}}

{{!-- File picker --}}
<file-picker type="image" name="img" value="{{img}}"></file-picker>

{{!-- Partials --}}
{{> "systems/my-system/templates/partials/ability-score.hbs" ability=system.abilities.str label="STR"}}
```

### ApplicationV2 Actions in Templates

```handlebars
{{!-- data-action maps to static ACTIONS --}}
<button type="button" data-action="rollAbility" data-ability="str">Roll STR</button>
<a data-action="editItem" data-item-id="{{item._id}}">Edit</a>
```

### Register Partials

```javascript
Hooks.once("init", async () => {
  await loadTemplates([
    "systems/my-system/templates/partials/ability-score.hbs",
    "systems/my-system/templates/partials/item-row.hbs"
  ]);
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
