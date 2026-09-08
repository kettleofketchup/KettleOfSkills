# Vault Metadata Model

Vault's data model is the part most API code gets wrong. Both the .NET SDK and the Vault Data
API expose the same underlying entities — understanding them once applies to both surfaces.

## Entity classes

Every object belongs to an entity class, identified by a short string code in the .NET API:

| Code | Entity | Edition |
|------|--------|---------|
| `FILE` | Files (and their versions) | All |
| `FLDR` | Folders | All |
| `ITEM` | Items — the engineering/BOM layer above files | Professional |
| `CO` | Change orders (ECOs) | Professional |
| `CUSTENT` | Custom objects | Professional |

These codes are the scoping argument for property calls:

```csharp
PropDef[] defs = webSvc.PropertyService.GetPropertyDefinitionsByEntityClassId("CUSTENT");
object[] vals  = webSvc.PropertyService.GetProperties("CUSTENT", entityIds, propDefIds);
```

VDF exposes the same thing as `VDF.Vault.Currency.Entities.EntityClassIds.Files` etc.

The Vault Data API does **not** use these codes — it returns an `entityType` field with
readable values (`"Item"`, `"ItemVersion"`, `"File"`). Do not map one to the other blindly
when porting code between the surfaces.

Entity classes also have **sub-classes** (e.g. a folder of type `Project`), which matter
because a UDP can be associated with a sub-class rather than the whole class.

## Properties: system vs user-defined

| Kind | Source | Identified by |
|------|--------|---------------|
| System property | Vault-managed (Name, Version, State, Revision, Created By, …) | stable `SysName`, well-known IDs in `PropertyDefinitionIds.Server` |
| UDP (user-defined property) | Vault administrator | `DispName`; **ID differs per Vault** |

**The single most important rule: never hardcode a `PropDefId`.** Property definition IDs are
assigned per-Vault and differ between dev, test, and production. Resolve them at runtime by
`SysName` (system properties) or `DispName` (UDPs). Hardcoded IDs are the usual cause of a
search that returns nothing while the file plainly exists in the client.

Via VDF the equivalent is `PropertyManager.GetPropertyDefinitions(entityClassId, filter,
PropertyDefinitionFilter.IncludeAll)` returning a `PropertyDefinitionDictionary`, then
`GetPropertyValue()`. Well-known definitions index directly, e.g.
`PropertyDefinitionIds.Server.LifeCycleDefinition`.

### UDP associations

Associations declare which entity classes may use a UDP. A UDP associated only with Change
Order can be used solely by change orders. **A UDP with no association appears nowhere** — not
in the client property grid, not on the entity via the API. When a newly created UDP reads
back as absent, check its associations before suspecting the API.

A UDP can only be deleted when it is associated with no category and used by no Vault object.

### Property mapping

Properties can be mapped so a value from a master file is written into a subordinate UDP.
Mapped values are written by the server on check-in — writing them directly through the API
can be overwritten on the next check-in.

## Categories

A category labels Vault data and drives the behaviour attached to it. Assigning a category
assigns, in one move:

- the set of UDPs available on the object
- a **lifecycle definition**
- a **revision scheme**
- security behaviours

Every object is always in a category: anything not explicitly assigned falls into the default
category for its entity class. Files, folders, items, and custom objects all participate.
Category is therefore the correct lever for bulk metadata changes — reassigning a category
changes properties, lifecycle, and revision scheme together, which is rarely what a naive
"set this one property" script intends.

## Lifecycles and states

A lifecycle definition is a state machine assigning security, behaviours, and properties based
on where an object sits in the design process. States are the nodes (`Work in Progress`,
`For Review`, `Released`); transitions are the edges.

Each transition carries:

- **Criteria** — property compliance conditions that must be satisfied before the change
- **Actions** — what fires during the change, e.g. a revision bump
- **Security** — who is permitted to make the change

A state change that fails is usually a criteria or permission failure, not an API error.
Read the returned restriction details rather than retrying.

API access: `.NET` via `DocumentService`/`ItemService` state-change calls and
`PropertyDefinitionIds.Server.LifeCycleDefinition`. REST lifecycle **reads and updates** for
files, folders, and items require **Vault 2027.1 or newer** — on older servers this work must
go through the .NET SDK.

## Versions vs revisions

These are distinct and routinely conflated:

- A **version** is created by every check-in. Sequential, automatic, unbounded.
- A **revision** is a deliberate milestone (A, B, C or 1, 2, 3 per the revision scheme),
  applied to a file/item and its related children as a revision level.

Revision schemes attach to categories, which attach to objects. Revision bumps are usually
automated by a lifecycle transition action — an admin configures, for example, a bump when a
file moves from Work In Progress to Review, and the transition editor offers primary,
secondary, and tertiary revision levels via *Bump Primary Revision*.

So: "get me the latest file" almost always means the latest **version**; "get me the released
drawing" means the latest **revision** at a released **state**. Filter on state, not on
version number.

## Items and BOMs

Items (Professional only) sit above files as the engineering record. One item may link to
several files; the item carries the part number, and the BOM structure lives on item versions,
not on files. BOM queries return `itemVersions`, `itemBomLinks`, `occurrences`, and
`bomComponents` — occurrences carry the quantity, links carry the structure. Reading a
CAD assembly's file relationships is not the same as reading its BOM.

## Practical ordering for any metadata task

1. Determine the entity class of the target.
2. Fetch property definitions for that class and resolve names to IDs at runtime.
3. Check the object's category — it determines which UDPs and lifecycle even apply.
4. For a state change, read the lifecycle definition and its transition criteria first.
5. Distinguish version from revision in the requirement before writing the query.
