---
name: go-bun
description: Bun SQL-first ORM for Go (uptrace/bun). Use for PostgreSQL/SQLite setup, bun.BaseModel struct tags, query builder CRUD, relations, migrations, fixtures, hooks, transactions, and soft deletes.
---

# Bun ORM for Go

Bun (`github.com/uptrace/bun`) is a SQL-first ORM for PostgreSQL, MySQL, MSSQL, and SQLite. It
wraps `database/sql`, so a `*bun.DB` exposes the full query builder plus standard `*sql.DB`
behaviour. Write SQL-shaped Go; Bun does not hide the SQL.

Validated against **Bun v1.2.18** (2026-02-28); requires **Go 1.24+**.

## When to use

Use when defining models, building queries, wiring relations, running migrations, seeding
fixtures, adding hooks/observability, managing transactions, or enabling soft deletes in a Go
project that uses Bun.

## Install

```bash
go get github.com/uptrace/bun
go get github.com/uptrace/bun/dialect/pgdialect      # or sqlitedialect
go get github.com/uptrace/bun/driver/pgdriver        # or driver/sqliteshim
go get github.com/uptrace/bun/extra/bundebug         # query logging (dev)
```

## Connect

PostgreSQL (Bun's own `pgdriver`):

```go
import (
    "database/sql"
    "github.com/uptrace/bun"
    "github.com/uptrace/bun/dialect/pgdialect"
    "github.com/uptrace/bun/driver/pgdriver"
)

dsn := "postgres://user:pass@localhost:5432/db?sslmode=disable"
sqldb := sql.OpenDB(pgdriver.NewConnector(pgdriver.WithDSN(dsn)))
db := bun.NewDB(sqldb, pgdialect.New(), bun.WithDiscardUnknownColumns())
```

`bun.WithDiscardUnknownColumns()` keeps the app resilient while migrations add/remove columns.
As an alternative driver, `pgx` works with `pgdialect` via `stdlib.OpenDB(cfg)` (set
`cfg.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol`) — useful if `pgdriver` misbehaves.

SQLite (`sqliteshim` auto-selects a pure-Go or cgo driver):

```go
import (
    "github.com/uptrace/bun/dialect/sqlitedialect"
    "github.com/uptrace/bun/driver/sqliteshim"
)

sqldb, err := sql.Open(sqliteshim.ShimName, "file:app.db?cache=shared")
db := bun.NewDB(sqldb, sqlitedialect.New())
db.SetMaxOpenConns(1) // required for file::memory:?cache=shared; mitigates file-DB "locked" too
```

Enable query logging in development (do not register in production unconditionally):

```go
import "github.com/uptrace/bun/extra/bundebug"
db.AddQueryHook(bundebug.NewQueryHook(
    bundebug.WithVerbose(true), bundebug.FromEnv("BUNDEBUG"))) // BUNDEBUG=1/2 toggles at runtime
```

Always pass a `context.Context` to terminal methods (`Scan`, `Exec`). Reuse a single `*bun.DB`
for the process; it is a connection pool. In production size it explicitly:
`n := 4 * runtime.GOMAXPROCS(0); sqldb.SetMaxOpenConns(n); sqldb.SetMaxIdleConns(n)`.

## Define a model

```go
type User struct {
    bun.BaseModel `bun:"table:users,alias:u"`

    ID        int64     `bun:"id,pk,autoincrement"`
    Name      string    `bun:"name,notnull"`
    Email     string    `bun:"email,unique"`
    CreatedAt time.Time `bun:"created_at,nullzero,notnull,default:current_timestamp"`
}
```

Key column tags: `pk`, `autoincrement`, `notnull`, `unique`, `nullzero` (write zero values as
`NULL`), `default:expr`, `type:...`, `scanonly`, `soft_delete`. See
`references/models-and-queries.md` for the full tag list and scanning patterns.

## Core CRUD

```go
// Insert (PK is populated back onto the struct)
_, err := db.NewInsert().Model(user).Exec(ctx)

// Select one
err := db.NewSelect().Model(user).Where("id = ?", id).Scan(ctx)

// Select many into a slice
var users []User
err := db.NewSelect().Model(&users).Where("name LIKE ?", "a%").Order("id").Scan(ctx)

// Update specific columns by PK
_, err := db.NewUpdate().Model(user).Column("name", "email").WherePK().Exec(ctx)

// Delete
_, err := db.NewDelete().Model(user).Where("id = ?", id).Exec(ctx)
```

Use `?` placeholders (never string concatenation). `bun.Ident("col")` quotes identifiers and
`bun.Safe(...)` injects trusted SQL fragments.

## Reference files

Load the matching reference for deeper work:

- `references/models-and-queries.md` — struct tags, query builder (joins, subqueries, CTEs,
  bulk insert, upsert, `Returning`), raw SQL, table creation.
- `references/relations.md` — has-one / has-many / belongs-to / many-to-many, `Relation()`
  eager loading with callbacks, manual joins, `RegisterModel` for m2m.
- `references/migrations.md` — `migrate.Migrations`, Go and SQL migrations, the `Migrator` API
  (`Init`/`Migrate`/`Rollback`/`CreateGoMigration`), and the urfave/cli command harness.
- `references/hooks-transactions-fixtures.md` — query hooks, model hooks
  (`BeforeAppendModel`, CRUD hooks), `RunInTx`, the `bun.IDB` pattern, soft deletes, and
  `dbfixture` seeding.
