---
name: charm-tui
description: Build Go terminal UIs (TUIs) and CLIs with charmbracelet — Bubble Tea runtime, Lip Gloss styling, Bubbles components, Glamour markdown, Harmonica animation, BubbleZone mouse. For any bubbletea TUI.
---

# Charm TUI stack for Go

Build terminal UIs and interactive CLIs in Go with [Charm](https://charm.sh) libraries. All
Charm libraries below are on **v2** and use the `charm.land/<lib>/v2` module path (v1 was
`github.com/charmbracelet/<lib>`). BubbleZone and Harmonica keep their `github.com` paths.

## Mental model: The Elm Architecture

Bubble Tea is the runtime; everything else plugs into it. A program is one `tea.Model`:

- **`Init() tea.Cmd`** — kick off startup work (timers, IO). Return `nil` for none.
- **`Update(tea.Msg) (tea.Model, tea.Cmd)`** — the *only* place state changes. A `Msg` arrives
  (keypress, tick, window resize, custom event), you return a new model and optionally a `Cmd`.
- **`View() tea.View`** — pure render of current state to a `tea.View` (v2 returns `tea.View`,
  not `string`). Never mutate state here.

`Cmd` = `func() tea.Msg`: run side effects off the render loop; their result comes back as a
`Msg` to `Update`. This unidirectional loop (Msg → Update → View) is the whole framework.

## Library map — pick by need

| Need | Library | Reference |
|------|---------|-----------|
| Event loop, program lifecycle, key/mouse/tick messages | Bubble Tea | `references/bubbletea.md` |
| Colors, borders, padding, alignment, tables/lists/trees | Lip Gloss | `references/lipgloss.md` |
| Ready-made widgets (input, list, table, viewport, spinner, progress) | Bubbles | `references/bubbles.md` |
| Render Markdown to styled ANSI | Glamour | `references/glamour.md` |
| Spring/physics-based motion for smooth animation | Harmonica | `references/harmonica.md` |
| Mouse hit-testing / clickable regions | BubbleZone | `references/bubblezone.md` |
| Composite recipes: scroll+mouse, tabs, clickable tabs, split panes | (assembled) | `references/patterns.md` |
| One palette across every widget (light/dark source of truth) | (shared) | `references/theming.md` |

## Install

```bash
go get charm.land/bubbletea/v2 charm.land/lipgloss/v2 charm.land/bubbles/v2 charm.land/glamour/v2
go get github.com/charmbracelet/harmonica github.com/lrstanley/bubblezone/v2
```

## Minimal complete program

```go
package main

import (
	"fmt"
	"os"

	tea "charm.land/bubbletea/v2"
	"charm.land/lipgloss/v2"
)

type model struct{ count int }

func (m model) Init() tea.Cmd { return nil }

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyPressMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "up", "k":
			m.count++
		case "down", "j":
			m.count--
		}
	}
	return m, nil
}

func (m model) View() tea.View {
	style := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("205"))
	v := tea.NewView(fmt.Sprintf("Count: %s\n\n↑/↓ to change · q to quit\n",
		style.Render(fmt.Sprintf("%d", m.count))))
	v.AltScreen = true // full-screen mode; omit for inline
	return v
}

func main() {
	if _, err := tea.NewProgram(model{}).Run(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
```

## Composing components (the key pattern)

Bubbles are themselves `Update`/`View` types. Embed them in your model, forward `Msg`s in
`Update`, and stitch their `View()` output with Lip Gloss:

```go
type model struct {
	input textinput.Model
	list  list.Model
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd
	var cmd tea.Cmd
	m.input, cmd = m.input.Update(msg) // forward to each child
	cmds = append(cmds, cmd)
	m.list, cmd = m.list.Update(msg)
	cmds = append(cmds, cmd)
	return m, tea.Batch(cmds...) // batch child commands
}

func (m model) View() tea.View {
	return tea.NewView(lipgloss.JoinVertical(lipgloss.Left, m.input.View(), m.list.View()))
}
```

## Rules that prevent most bugs

- **Never do IO in `Update`/`View` directly.** Wrap it in a `Cmd` so the loop stays responsive.
- **`View()` is pure** — read state, return a view, mutate nothing.
- **Handle `tea.WindowSizeMsg`** to size viewports/lists; components need explicit sizes.
- **A `Cmd` returning `nil` is a no-op.** Combine several with `tea.Batch`; sequence with
  `tea.Sequence`.
- **Enable mouse per-view** via `v.MouseMode = tea.MouseModeCellMotion` (see BubbleZone ref).
- Use `lipgloss.Println`/`Sprint` (not `fmt`) when printing styled text so colors downsample to
  the terminal's capabilities.

See each reference file for full APIs and worked examples.
