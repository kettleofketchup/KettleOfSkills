# Relations

Bun does not auto-join. Declare relations with `bun` struct tags, then load them explicitly
with `.Relation("Field")`. The `join:` clause maps `base_column=related_column`.

## Has-one

Parent holds the foreign key target; one related row.

```go
type User struct {
    bun.BaseModel `bun:"table:users,alias:u"`
    ID      int64
    Profile *Profile `bun:"rel:has-one,join:id=user_id"`
}
type Profile struct {
    ID     int64
    UserID int64
    Bio    string
}
```

## Belongs-to

Child holds the foreign key; resolves to the parent it belongs to.

```go
type Comment struct {
    ID       int64
    AuthorID int64
    Author   *User `bun:"rel:belongs-to,join:author_id=id"`
}
```

`has-one` vs `belongs-to`: pick by **which table holds the FK column**. If the related table's
column points back to this model, use `has-one`; if this model's column points at the related
table, use `belongs-to`.

## Has-many

Parent owns a slice of children keyed by an FK on the child.

```go
type User struct {
    bun.BaseModel `bun:"table:users,alias:u"`
    ID    int64
    Posts []*Post `bun:"rel:has-many,join:id=user_id"`
}
```

## Many-to-many

Requires an explicit join model registered before use. The `m2m:` tag names the join table; the
`join:` clause references **field names in the join model**, not columns.

```go
type Order struct {
    bun.BaseModel `bun:"table:orders,alias:o"`
    ID    int64
    Items []Item `bun:"m2m:order_to_items,join:Order=Item"`
}
type Item struct {
    bun.BaseModel `bun:"table:items,alias:i"`
    ID int64
}
type OrderToItem struct {
    OrderID int64  `bun:",pk"`
    Order   *Order `bun:"rel:belongs-to,join:order_id=id"`
    ItemID  int64  `bun:",pk"`
    Item    *Item  `bun:"rel:belongs-to,join:item_id=id"`
}

// Register the junction model once, after creating db:
db.RegisterModel((*OrderToItem)(nil))
```

## Eager loading

```go
// Load one relation
err := db.NewSelect().Model(&users).Relation("Posts").Scan(ctx)

// Nested relations via dotted path
err = db.NewSelect().Model(&users).Relation("Posts.Comments").Scan(ctx)

// Filter / shape a relation with a callback
err = db.NewSelect().Model(&users).
    Relation("Posts", func(q *bun.SelectQuery) *bun.SelectQuery {
        return q.Where("published").Order("created_at DESC").Limit(5)
    }).
    Scan(ctx)

// Select specific columns of a relation
err = db.NewSelect().Model(&comments).
    Relation("Author", func(q *bun.SelectQuery) *bun.SelectQuery {
        return q.Column("id", "name")
    }).Scan(ctx)
```

## Polymorphic has-many

```go
type Comment struct {
    ID            int64
    TrackableID   int64
    TrackableType string
}
type Article struct {
    ID       int64
    Comments []Comment `bun:"rel:has-many,join:id=trackable_id,join:type=trackable_type,polymorphic"`
}
```

Bun automatically adds `WHERE trackable_type = '<value>'`, where `<value>` derives from the
parent's table/model name. Pin it explicitly with `polymorphic:custom_name` rather than relying
on the default pluralization.

## Relation tips

- **No N+1.** `.Relation(...)` does not loop per parent: Bun issues one extra `WHERE ... IN (ids)`
  query per relation (or a JOIN for belongs-to/has-one), so eager-loading a slice is efficient.
- **Static filters in the tag.** Add `join_on:` to constrain the join without a per-query
  callback, e.g. `bun:"rel:has-many,join:id=user_id,join_on:active = true"`.
- **Real FK constraints are opt-in.** Relation tags do not create database foreign keys. For
  `ON DELETE`/`ON UPDATE`, add `on_delete:CASCADE,on_update:CASCADE` to the tag and call
  `NewCreateTable().Model(...).WithForeignKeys()`.
- **Self-references** (e.g. user-follows-user) use the same patterns; an m2m self-relation still
  needs its join model registered via `db.RegisterModel`.

## When relations are not enough

For arbitrary joins, skip relation tags and write `Join(...)` manually (see
models-and-queries.md). Relations are for the common ownership patterns; complex reporting
queries are usually clearer with explicit joins and `ColumnExpr`.
