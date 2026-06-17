# Migrations

Bun migrations live in their own package, run in **groups** (one `migrate` applies all pending
migrations as a group; one `rollback` reverts the last group), and track state in the
`bun_migrations` table.

## Migration collection

```go
package migrations

import "github.com/uptrace/bun/migrate"

var Migrations = migrate.NewMigrations()
```

## Go-based migrations

One file per migration, registered in `init()`. `MustRegister(up, down)`:

```go
package migrations

import (
    "context"
    "github.com/uptrace/bun"
)

func init() {
    Migrations.MustRegister(func(ctx context.Context, db *bun.DB) error {
        _, err := db.NewCreateTable().Model((*User)(nil)).IfNotExists().Exec(ctx)
        return err
    }, func(ctx context.Context, db *bun.DB) error {
        _, err := db.NewDropTable().Model((*User)(nil)).IfExists().Exec(ctx)
        return err
    })
}
```

Generate a timestamped stub: `migrator.CreateGoMigration(ctx, "create_users")`.

## SQL-based migrations

Embed `*.sql` files; name them `<timestamp>_<name>.up.sql` / `.down.sql`. Use `.tx.up.sql` to
wrap a file in a transaction, and `--bun:split` to separate statements within a file.

```go
import "embed"

//go:embed *.sql
var sqlMigrations embed.FS

func init() {
    if err := Migrations.Discover(sqlMigrations); err != nil {
        panic(err)
    }
}
```

Generate paired SQL stubs: `migrator.CreateSQLMigrations(ctx, "add_index")`.

## Migrator API

```go
import "github.com/uptrace/bun/migrate"

migrator := migrate.NewMigrator(db, migrations.Migrations)

// One-time: create bun_migrations / bun_migration_locks tables
if err := migrator.Init(ctx); err != nil { return err }

// Apply pending migrations (lock to prevent concurrent runs)
if err := migrator.Lock(ctx); err != nil { return err }
defer migrator.Unlock(ctx)

group, err := migrator.Migrate(ctx)
if err != nil { return err }
if group.IsZero() {
    fmt.Println("no new migrations to run")
} else {
    fmt.Printf("migrated to %s\n", group)
}

// Revert the last applied group
group, err = migrator.Rollback(ctx)

// Inspect status
ms, err := migrator.MigrationsWithStatus(ctx)
fmt.Println("applied:", ms.Applied(), "unapplied:", ms.Unapplied())
```

## CLI harness (urfave/cli v2)

The canonical Bun starter wires the migrator into a `db` command group. Minimal shape:

```go
import (
    "github.com/uptrace/bun/migrate"
    "github.com/urfave/cli/v2"
)

func newDBCommand(migrator *migrate.Migrator) *cli.Command {
    return &cli.Command{
        Name: "db",
        Subcommands: []*cli.Command{
            {Name: "init", Action: func(c *cli.Context) error {
                return migrator.Init(c.Context)
            }},
            {Name: "migrate", Action: func(c *cli.Context) error {
                if err := migrator.Lock(c.Context); err != nil { return err }
                defer migrator.Unlock(c.Context)
                group, err := migrator.Migrate(c.Context)
                if err != nil { return err }
                if group.IsZero() { fmt.Println("nothing to migrate"); return nil }
                fmt.Printf("migrated to %s\n", group)
                return nil
            }},
            {Name: "rollback", Action: func(c *cli.Context) error {
                if err := migrator.Lock(c.Context); err != nil { return err }
                defer migrator.Unlock(c.Context)
                group, err := migrator.Rollback(c.Context)
                if err != nil { return err }
                if group.IsZero() { fmt.Println("nothing to rollback"); return nil }
                fmt.Printf("rolled back %s\n", group)
                return nil
            }},
            {Name: "create_go", Action: func(c *cli.Context) error {
                _, err := migrator.CreateGoMigration(c.Context, c.Args().Get(0))
                return err
            }},
            {Name: "create_sql", Action: func(c *cli.Context) error {
                _, err := migrator.CreateSQLMigrations(c.Context, c.Args().Get(0))
                return err
            }},
            {Name: "status", Action: func(c *cli.Context) error {
                ms, err := migrator.MigrationsWithStatus(c.Context)
                if err != nil { return err }
                fmt.Printf("unapplied: %s\nlast group: %s\n", ms.Unapplied(), ms.LastGroup())
                return nil
            }},
        },
    }
}
```

Run with `go run . db init`, `db migrate`, `db rollback`, `db create_sql add_users`, `db status`.
The full upstream example (`example/migrate/main.go`) adds `lock`, `unlock`, `create_tx_sql`,
and `mark_applied`. Use `migrate.WithMarkAppliedOnSuccess(true)` or `migrate.WithNopMigration`
for advanced cases.
