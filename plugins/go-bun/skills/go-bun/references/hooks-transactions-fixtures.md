# Hooks, Transactions, Soft Deletes & Fixtures

## Query hooks

Implement `bun.QueryHook` for cross-cutting concerns (logging, tracing, metrics). Register with
`db.AddQueryHook`.

```go
type logHook struct{}

func (logHook) BeforeQuery(ctx context.Context, e *bun.QueryEvent) context.Context {
    return ctx
}
func (logHook) AfterQuery(ctx context.Context, e *bun.QueryEvent) {
    log.Printf("%s [%s]", e.Query, time.Since(e.StartTime))
}

db.AddQueryHook(logHook{})
```

Ready-made hooks:
- `github.com/uptrace/bun/extra/bundebug` — pretty query logging in dev:
  `db.AddQueryHook(bundebug.NewQueryHook(bundebug.WithVerbose(true)))`.
- `github.com/uptrace/bun/extra/bunotel` — OpenTelemetry tracing/metrics:
  `db.AddQueryHook(bunotel.NewQueryHook(bunotel.WithDBName("app")))`.

## Model hooks

`BeforeAppendModel` is the most useful — it fires while the insert/update query is built, so it
is the idiomatic place to stamp timestamps:

```go
var _ bun.BeforeAppendModelHook = (*User)(nil)

func (u *User) BeforeAppendModel(ctx context.Context, query bun.Query) error {
    switch query.(type) {
    case *bun.InsertQuery:
        u.CreatedAt = time.Now()
    case *bun.UpdateQuery:
        u.UpdatedAt = time.Now()
    }
    return nil
}
```

CRUD hooks run around query execution; declare the interface assertion so the compiler verifies
the signature (e.g. `var _ bun.AfterSelectHook = (*User)(nil)` with
`func (u *User) AfterSelect(ctx context.Context, q *bun.SelectQuery) error`). Available:
`Before/AfterSelect`, `Before/AfterInsert`, `Before/AfterUpdate`, `Before/AfterDelete`,
`Before/AfterScanRow`, plus DDL `Before/AfterCreateTable` and `Before/AfterDropTable`.

## Transactions

`RunInTx` is the default: it commits on `nil` and rolls back on any error or panic.

```go
err := db.RunInTx(ctx, &sql.TxOptions{}, func(ctx context.Context, tx bun.Tx) error {
    if _, err := tx.NewInsert().Model(order).Exec(ctx); err != nil {
        return err
    }
    _, err := tx.NewUpdate().Model(account).Set("balance = balance - ?", amt).
        WherePK().Exec(ctx)
    return err
})
```

Manual control when needed: `tx, err := db.BeginTx(ctx, &sql.TxOptions{})`, then
`defer tx.Rollback()` (a no-op after a successful `tx.Commit()`).

### Write transaction-agnostic helpers with `bun.IDB`

`*bun.DB`, `bun.Tx`, and `bun.Conn` all satisfy `bun.IDB`. Accept it so a function works inside
or outside a transaction:

```go
func CreateUser(ctx context.Context, db bun.IDB, u *User) error {
    _, err := db.NewInsert().Model(u).Exec(ctx)
    return err
}
// CreateUser(ctx, db, u)  — standalone
// CreateUser(ctx, tx, u)  — inside RunInTx
```

## Soft deletes

Add a `soft_delete` timestamp field. `NewDelete` then issues an `UPDATE ... SET deleted_at`,
and `NewSelect` auto-filters `deleted_at IS NULL`.

```go
type User struct {
    ID        int64
    DeletedAt time.Time `bun:",soft_delete,nullzero"`
}

db.NewDelete().Model(u).Where("id = ?", id).Exec(ctx)              // soft delete
db.NewSelect().Model(&users).Scan(ctx)                            // excludes deleted
db.NewSelect().Model(&users).WhereDeleted().Scan(ctx)             // only deleted
db.NewSelect().Model(&users).WhereAllWithDeleted().Scan(ctx)      // include all
db.NewDelete().Model(u).Where("id = ?", id).ForceDelete().Exec(ctx) // hard delete
```

## Fixtures (seeding & test data)

`github.com/uptrace/bun/dbfixture` loads YAML fixtures, with model cross-references and Go
templates.

```go
import (
    "embed"
    "text/template"
    "github.com/uptrace/bun/dbfixture"
)

//go:embed fixtures/*.yml
var fixtureFS embed.FS

db.RegisterModel((*User)(nil), (*Org)(nil)) // register models used in fixtures

fixture := dbfixture.New(db,
    dbfixture.WithRecreateTables(),   // drop+create (tests) — or WithTruncateTables()
    dbfixture.WithTemplateFuncs(template.FuncMap{
        "now": func() string { return time.Now().Format(time.RFC3339Nano) },
    }),
)
if err := fixture.Load(ctx, fixtureFS, "fixtures/seed.yml"); err != nil {
    return err
}

smith := fixture.MustRow("User.smith").(*User) // fetch a named row back
```

`fixtures/seed.yml`:

```yaml
- model: User
  rows:
    - _id: smith                 # name this row for references
      name: John Smith
      email: john@smith.com
      created_at: '{{ now }}'

- model: Org
  rows:
    - name: "{{ $.User.smith.Name }}'s Org"   # reference a loaded row's field
      owner_id: '{{ $.User.smith.ID }}'
```

`_id` names a row; `$.Model.rowID.Field` references previously loaded data;
`{{ ... }}` uses `text/template` with any functions registered via `WithTemplateFuncs`.
