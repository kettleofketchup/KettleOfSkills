# Composite patterns / recipes

Common TUI layouts that no single library ships as a drop-in — you assemble them from the
primitives. All snippets verified against v2.

## Scrollable area with mouse-wheel support

The Bubbles `viewport` handles scrolling — keyboard (via its `KeyMap`) **and** the mouse wheel.
Mouse-wheel support is built in: `MouseWheelEnabled` defaults to `true` and the component
consumes `tea.MouseWheelMsg` in its `Update`. You only need to (1) enable mouse mode on the
returned `tea.View`, and (2) forward every message to `vp.Update`.

```go
type model struct{ vp viewport.Model }

func initial() model {
	vp := viewport.New()
	vp.SetWidth(80)
	vp.SetHeight(20)
	vp.Style = lipgloss.NewStyle().Border(lipgloss.RoundedBorder())
	vp.SetContent(longText)
	// vp.MouseWheelEnabled is already true; vp.MouseWheelDelta defaults to 3 lines.
	return model{vp: vp}
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.vp.SetWidth(msg.Width)
		m.vp.SetHeight(msg.Height - 1)
	case tea.KeyPressMsg:
		if msg.String() == "q" || msg.String() == "ctrl+c" {
			return m, tea.Quit
		}
	}
	var cmd tea.Cmd
	m.vp, cmd = m.vp.Update(msg) // wheel + ↑/↓/pgup/pgdn handled here
	return m, cmd
}

func (m model) View() tea.View {
	v := tea.NewView(m.vp.View())
	v.MouseMode = tea.MouseModeCellMotion // REQUIRED — no mouse events reach vp without this
	return v
}
```

Programmatic control: `vp.ScrollUp(n)`, `vp.ScrollDown(n)`, `vp.PageDown()`, `vp.HalfPageUp()`,
`vp.GotoTop()`, `vp.GotoBottom()`. Read position with `vp.ScrollPercent()`,
`vp.AtTop()`, `vp.AtBottom()`.

## Tab bar (keyboard)

No tabs component exists — build one with Lip Gloss borders. The trick is an active-tab border
whose **bottom edge is blank** (`Bottom: " "`) with inward corners, so the selected tab visually
merges into the content pane below it.

```go
var (
	tabBorder = lipgloss.Border{
		Top: "─", Bottom: "─", Left: "│", Right: "│",
		TopLeft: "╭", TopRight: "╮", BottomLeft: "┴", BottomRight: "┴",
	}
	activeTabBorder = lipgloss.Border{ // note the blank Bottom + notch corners
		Top: "─", Bottom: " ", Left: "│", Right: "│",
		TopLeft: "╭", TopRight: "╮", BottomLeft: "┘", BottomRight: "└",
	}
	// These border glyphs + style colors are the theme injection points — see theming.md.
	tab       = lipgloss.NewStyle().Border(tabBorder, true).Padding(0, 1)
	activeTab = tab.Border(activeTabBorder, true)
	pane      = lipgloss.NewStyle().Border(lipgloss.NormalBorder()).Padding(1, 2)
)

type model struct {
	tabs   []string
	active int
	body   []string // content per tab
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	if k, ok := msg.(tea.KeyPressMsg); ok {
		switch k.String() {
		case "tab", "right", "l":
			m.active = (m.active + 1) % len(m.tabs)
		case "shift+tab", "left", "h":
			m.active = (m.active - 1 + len(m.tabs)) % len(m.tabs)
		case "q", "ctrl+c":
			return m, tea.Quit
		}
	}
	return m, nil
}

func (m model) View() tea.View {
	var rendered []string
	for i, t := range m.tabs {
		if i == m.active {
			rendered = append(rendered, activeTab.Render(t))
		} else {
			rendered = append(rendered, tab.Render(t))
		}
	}
	row := lipgloss.JoinHorizontal(lipgloss.Bottom, rendered...)
	content := pane.Width(lipgloss.Width(row) - 2).Render(m.body[m.active])
	return tea.NewView(lipgloss.JoinVertical(lipgloss.Left, row, content))
}
```

## Clickable tabs (mouse)

Add BubbleZone to make the tabs above clickable — mark each tab, scan the root view, and
hit-test clicks. This is the same tab bar plus three lines (see `bubblezone.md`).

```go
// main(): zone.NewGlobal()

// In View(), wrap each tab with a unique id before joining:
rendered = append(rendered, zone.Mark("tab:"+t, style.Render(t)))
// ...build view as above, then Scan the OUTERMOST string:
v := tea.NewView(zone.Scan(lipgloss.JoinVertical(lipgloss.Left, row, content)))
v.MouseMode = tea.MouseModeCellMotion
return v

// In Update(), test clicks against each tab zone:
case tea.MouseClickMsg:
	for i, t := range m.tabs {
		if zone.Get("tab:" + t).InBounds(msg) {
			m.active = i
		}
	}
```

## Split panes

Size children from `tea.WindowSizeMsg`, render each, and stitch with Lip Gloss. Track a `focus`
field and forward key messages only to the focused child; forward mouse/size messages to all.

```go
left := leftStyle.Width(m.width/3).Height(m.height).Render(m.sidebar.View())
right := rightStyle.Width(m.width - m.width/3).Height(m.height).Render(m.main.View())
return tea.NewView(lipgloss.JoinHorizontal(lipgloss.Top, left, right))
```

Remember to subtract each style's `GetHorizontalFrameSize()`/`GetVerticalFrameSize()` from the
inner component's size so borders and padding don't overflow the terminal.
