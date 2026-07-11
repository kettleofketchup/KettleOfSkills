# Bubble Tea — the runtime

Module: `charm.land/bubbletea/v2` (imported as `tea`). The event loop that drives every Charm
TUI. Based on The Elm Architecture: `Msg → Update → View`.

## The Model interface

```go
type Model interface {
	Init() tea.Cmd
	Update(tea.Msg) (tea.Model, tea.Cmd)
	View() tea.View
}
```

`Update` returns a **new** model (value semantics — mutate the copy, return it). Store child
components as fields and reassign them from their `Update` return.

## tea.View (v2)

`View()` returns `tea.View`, not a string. Build one with `tea.NewView(content string)` and set
fields to control the terminal:

```go
func (m model) View() tea.View {
	v := tea.NewView(m.body())
	v.AltScreen = true                     // alternate screen buffer (full-screen app)
	v.MouseMode = tea.MouseModeCellMotion   // MouseModeNone | CellMotion | AllMotion
	v.WindowTitle = "My App"
	return v
}
```

`v.BackgroundColor` / `v.ForegroundColor` are `color.Color` terminal-level theme knobs — drive
them from the same palette as everything else (see `references/theming.md`).

Omit `AltScreen` (default false) for an inline program that renders in place and leaves output
in scrollback on exit.

## Messages (tea.Msg)

`Msg` is `any`. Handle with a type switch in `Update`:

| Msg type | Meaning | Access |
|----------|---------|--------|
| `tea.KeyPressMsg` | key pressed | `msg.String()` → `"enter"`, `"ctrl+c"`, `"up"`, `"a"` |
| `tea.KeyReleaseMsg` | key released (if enhanced keyboard) | `msg.String()` |
| `tea.MouseClickMsg` / `tea.MouseReleaseMsg` / `tea.MouseMotionMsg` / `tea.MouseWheelMsg` | mouse | `msg.Mouse()` → `.X`, `.Y`, `.Button` |
| `tea.MouseMsg` | interface all mouse msgs satisfy | `msg.Mouse()` |
| `tea.WindowSizeMsg` | terminal resized (also sent once at start) | `msg.Width`, `msg.Height` |
| `tea.FocusMsg` / `tea.BlurMsg` | terminal focus changed | — |

```go
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height
	case tea.KeyPressMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		}
	case tea.MouseClickMsg:
		mouse := msg.Mouse()
		_ = mouse.X // clicked column
	}
	return m, nil
}
```

Define **custom messages** as any type and deliver them from a `Cmd`:

```go
type dataLoadedMsg struct{ rows []Row }

func loadData() tea.Cmd {
	return func() tea.Msg {
		rows := query() // slow IO happens off the render loop
		return dataLoadedMsg{rows}
	}
}
// In Update: case dataLoadedMsg: m.rows = msg.rows
```

## Commands (tea.Cmd)

`Cmd` = `func() tea.Msg`. Bubble Tea runs it in a goroutine and feeds the result back to
`Update`. This is how *all* side effects (IO, timers, spawning processes) happen.

| Command | Use |
|---------|-----|
| `tea.Quit` | exit the program (it *is* a Cmd, don't call it) |
| `tea.Batch(cmds...)` | run several Cmds concurrently, order-independent |
| `tea.Sequence(cmds...)` | run Cmds one after another, in order |
| `tea.Tick(d, fn)` | fire `fn(t)` once after duration `d` (re-issue for a loop) |
| `tea.Every(d, fn)` | fire on a wall-clock-aligned interval |

**Not commands in v2** (these were v1 `Cmd`s — they moved):

- **Print above the TUI:** call `p.Println(...)` / `p.Printf(...)` on the `*Program` (unmanaged
  output; suppressed while AltScreen is active). There is no `tea.Printf`/`tea.Println` command.
- **Terminal title:** set `v.WindowTitle` on the `tea.View` you return (shown above).
- **Toggle full-screen at runtime:** set/unset `v.AltScreen` on the returned `tea.View` — there
  is no `tea.EnterAltScreen`/`tea.ExitAltScreen`.

Repeating timer via Tick:

```go
type tickMsg time.Time
func tick() tea.Cmd {
	return tea.Tick(time.Second, func(t time.Time) tea.Msg { return tickMsg(t) })
}
// Init returns tick(); Update's case tickMsg returns m, tick() to keep going.
```

## Running the program

```go
p := tea.NewProgram(initialModel())
finalModel, err := p.Run() // blocks until Quit; finalModel is your model's last state
```

Common `tea.NewProgram` options:

- `tea.WithContext(ctx)` — cancel the program when `ctx` is done.
- `tea.WithInput(r)` / `tea.WithOutput(w)` — redirect IO (tests, pipes).
- `tea.WithFilter(fn)` — intercept every Msg (e.g. block quit until saved).

Send messages from outside the loop with `p.Send(msg)` (e.g. from a background goroutine or a
network handler). Kill from outside with `p.Quit()` or `p.Kill()`.

## Nesting models

A parent model holds child models as fields, forwards relevant `Msg`s to each child's `Update`,
collects their `Cmd`s with `tea.Batch`, and composes their `View()` strings with Lip Gloss.
Route input by focus: track which child is active and only forward key messages to it. This is
the standard way to build multi-pane apps (see `references/bubbles.md` for component embedding).
