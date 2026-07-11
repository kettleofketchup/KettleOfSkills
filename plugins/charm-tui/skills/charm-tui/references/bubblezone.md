# BubbleZone — mouse zones for Bubble Tea

Module: `github.com/lrstanley/bubblezone/v2` (imported as `zone`). Bubble Tea gives you raw
mouse X/Y; BubbleZone lets you mark named regions in your `View()` and hit-test mouse events
against them — no manual coordinate math. Essential for clickable buttons, tabs, and lists.

## How it works (three steps)

1. **Initialize once** in `main()`: `zone.NewGlobal()`.
2. **Mark** each interactive region in `View()`: `zone.Mark("id", content)`. This wraps the
   string in invisible markers.
3. **Scan** the final composed view at the root: `zone.Scan(rootView)`. This records where every
   marked region ended up and strips the markers. Then in `Update`, test mouse events with
   `zone.Get("id").InBounds(msg)`.

`Mark` and `Scan` work together: `Mark` tags, `Scan` measures. You must call `Scan` on the
*outermost* rendered string exactly once per frame, after all `Mark`s and all Lip Gloss layout.

## Setup

```go
import (
	tea "charm.land/bubbletea/v2"
	"charm.land/lipgloss/v2"
	zone "github.com/lrstanley/bubblezone/v2"
)

func main() {
	zone.NewGlobal() // enables the global zone manager
	if _, err := tea.NewProgram(model{}).Run(); err != nil {
		log.Fatal(err)
	}
}
```

## Marking and scanning

```go
func (m model) View() tea.View {
	ok     := lipgloss.NewStyle().Padding(0, 2).Background(lipgloss.Color("36")).Render("OK")
	cancel := lipgloss.NewStyle().Padding(0, 2).Background(lipgloss.Color("203")).Render("Cancel")

	buttons := lipgloss.JoinHorizontal(lipgloss.Top,
		zone.Mark("ok", ok),         // tag each region with a unique id
		"  ",
		zone.Mark("cancel", cancel),
	)

	v := tea.NewView(zone.Scan(buttons)) // Scan the OUTERMOST view, once
	v.MouseMode = tea.MouseModeCellMotion // enable mouse (CellMotion or AllMotion)
	return v
}
```

## Hit-testing in Update

```go
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.MouseClickMsg: // or tea.MouseReleaseMsg for click-release semantics
		if zone.Get("ok").InBounds(msg) {
			return m, submit
		}
		if zone.Get("cancel").InBounds(msg) {
			return m, tea.Quit
		}
	case tea.KeyPressMsg:
		if msg.String() == "ctrl+c" {
			return m, tea.Quit
		}
	}
	return m, nil
}
```

`zone.Get(id)` returns a `*ZoneInfo`. Besides `InBounds(mouseMsg)`:

- `x, y := zone.Get(id).Pos(msg)` — mouse position **relative** to the zone's top-left (handy
  for clicking a specific row/cell inside a marked block).
- A zone that hasn't been scanned yet (e.g. off-screen) reports `InBounds` false safely.

## Nested components

Give each child component a unique id prefix so ids don't collide (e.g. `"tab:"+name`,
`fmt.Sprintf("row:%d", i)`). A child's `View()` can `zone.Mark` its own regions; only the root
model calls `zone.Scan`. This lets reusable components expose clickable areas without knowing
where they'll be placed.

```go
for i, item := range m.items {
	rows = append(rows, zone.Mark(fmt.Sprintf("row:%d", i), render(item)))
}
// In Update, loop ids to find which row was clicked:
for i := range m.items {
	if zone.Get(fmt.Sprintf("row:%d", i)).InBounds(msg) { m.cursor = i }
}
```

## Gotchas

- **Forgot `zone.Scan`?** All `InBounds` calls return false — nothing is clickable. Scan the
  root view every frame.
- **Enable mouse** via `v.MouseMode` on the returned `tea.View`, or zones never receive events.
- **Unique ids** — duplicate ids across regions make hit-testing ambiguous.
- Use a non-global manager (`zone.New()`, passed as a dependency) instead of `NewGlobal()` when
  running multiple independent programs in one process or writing tests.
