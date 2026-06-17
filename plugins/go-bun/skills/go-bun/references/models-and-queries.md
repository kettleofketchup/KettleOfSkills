# Models & Query Builder

## Struct tags

The first tag value is the column name (omit to use the snake_case field name).

| Tag | Effect |
|-----|--------|
| `pk` | Primary key (composite: tag multiple fields) |
| `autoincrement` | Auto-increment / serial PK |
| `notnull` | `NOT NULL` |
| `unique` / `unique:group` | Unique, optionally a named composite group |
| `nullzero` | Write Go zero value as `NULL` (pairs with `default:`) |
| `default:expr` | DDL default, e.g. `default:current_timestamp` |
| `type:varchar(100)` | Override the SQL column type |
| `scanonly` | Field is scanned but never written in queries |
| `soft_delete` | Marks the soft-delete timestamp column |
| `array` | Store a slice as a native PostgreSQL array |
| `rel:...` / `m2m:...` | Relations (see relations.md) |
| `-` (as `bun:"-"`) | Ignore the field entirely |
| `extend` | Embed/extend a base model's columns |

`bun.BaseModel` carries the table name and alias: `bun:"table:users,alias:u"`. Embed it as the
first field. For embedded structs, tag with `bun:",embed:prefix_"` to prefix child columns.

## Selecting

```go
err := db.NewSelect().Model(&users).
    Column("id", "name").                  // or ColumnExpr("count(*) AS n")
    Where("created_at > ?", since).
    WhereOr("name = ?", "root").
    Group("name").Having("count(*) > ?", 1).
    OrderExpr("id DESC").
    Limit(20).Offset(40).
    Scan(ctx)

// Scalars / aggregates
count, err := db.NewSelect().Model((*User)(nil)).Count(ctx)
exists, err := db.NewSelect().Model((*User)(nil)).Where("id = ?", id).Exists(ctx)

// Scan into non-model destinations
var names []string
err = db.NewSelect().Model((*User)(nil)).Column("name").Scan(ctx, &names)
```

Placeholders: positional `?`, named via `bun.Ident`/`bun.Safe`, and `?TableName`,
`?TableAlias`, `?PKs`, `?Columns` model placeholders inside `ColumnExpr`/`Where`.

Handy select extras:

```go
// Paginate in one round-trip (applies LIMIT, returns total count)
total, err := db.NewSelect().Model(&users).Limit(20).Offset(40).ScanAndCount(ctx)

// IN with a Go slice (NOT a subquery) — use bun.In
err = db.NewSelect().Model(&users).Where("id IN (?)", bun.In([]int64{1, 2, 3})).Scan(ctx)
```

- `Apply(func(q *bun.SelectQuery) *bun.SelectQuery)` injects reusable/conditional fragments.
- `WhereGroup(" AND ", func(q) ...)` wraps mixed `Where`/`WhereOr` in parentheses to avoid
  AND/OR precedence bugs.

## Joins & subqueries

```go
// Manual join (no relation needed)
err := db.NewSelect().Model(&books).
    Join("JOIN authors AS a ON a.id = book.author_id").
    Where("a.name = ?", name).
    Scan(ctx)

// Subquery
sub := db.NewSelect().Model((*User)(nil)).Column("id").Where("active")
err = db.NewSelect().Model(&orders).Where("user_id IN (?)", sub).Scan(ctx)

// CTE
err = db.NewSelect().
    With("recent", db.NewSelect().Model((*User)(nil)).Where("created_at > ?", since)).
    Table("recent").Scan(ctx, &users)
```

## Inserting

```go
// Single or bulk (pass a slice)
_, err := db.NewInsert().Model(&users).Exec(ctx)

// Upsert — PostgreSQL
_, err = db.NewInsert().Model(user).
    On("CONFLICT (email) DO UPDATE").
    Set("name = EXCLUDED.name").
    Exec(ctx)

// Upsert — SQLite uses the same ON CONFLICT syntax.
// Return generated columns (PG/SQLite):
_, err = db.NewInsert().Model(user).Returning("id, created_at").Exec(ctx)

// Insert from a SELECT (the source CTE must be named in Table)
_, err = db.NewInsert().Model((*Archive)(nil)).
    With("src", db.NewSelect().Model((*User)(nil))).
    Table("src").
    Exec(ctx)

// Insert and ignore conflicts (ON CONFLICT DO NOTHING / INSERT IGNORE)
_, err = db.NewInsert().Model(&users).Ignore().Exec(ctx)
```

## Updating

```go
// Whitelist columns (safer than sending every field)
_, err := db.NewUpdate().Model(user).Column("name").WherePK().Exec(ctx)

// Expression update without loading the row
_, err = db.NewUpdate().Model((*User)(nil)).
    Set("login_count = login_count + 1").
    Where("id = ?", id).Exec(ctx)

// Bulk update from values
_, err = db.NewUpdate().Model(&users).Column("name").Bulk().Exec(ctx)
```

`OmitZero()` skips zero-valued columns on update. `WherePK()` builds the `WHERE` from the
model's primary key(s).

## Deleting

```go
_, err := db.NewDelete().Model((*User)(nil)).Where("id = ?", id).Exec(ctx)
res, err := db.NewDelete().Model(user).WherePK().Exec(ctx)
n, _ := res.RowsAffected()
```

## Raw SQL & table DDL

```go
// Raw query mapped onto a model/dest
err := db.NewRaw("SELECT * FROM users WHERE id = ?", id).Scan(ctx, &user)

// Create/drop tables from the model definition (handy for tests)
_, err = db.NewCreateTable().Model((*User)(nil)).IfNotExists().Exec(ctx)
_, err = db.NewDropTable().Model((*User)(nil)).IfExists().Cascade().Exec(ctx)
```

Prefer migrations over `NewCreateTable` for production schemas (see migrations.md).
