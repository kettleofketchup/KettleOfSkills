---
description: Legacy Application v1 ActorSheet, Handlebars template syntax, helpers, partials
last_updated: 2026-03-18
---

# Legacy Sheets & Handlebars Templates

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

  async _onRollAbility(event) {
    const ability = event.currentTarget.dataset.ability;
    await this.actor.rollAbility(ability);
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

### Custom Handlebars Helpers

```javascript
Handlebars.registerHelper("capitalize", (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1);
});

Handlebars.registerHelper("add", (a, b) => a + b);

// Usage: {{capitalize system.alignment}}, {{add system.level 1}}
```
