# Bubbles — ready-made components

Module: `charm.land/bubbles/v2`. Each component is its own `Update`/`View` type that you embed
in your model. The contract is always the same: **construct → forward `Msg`s in `Update` →
render with `View()` → read state via getters**. To color every component from one palette
(delegate `Styles`, table/help `Styles`, textinput `SetStyles`, `viewport.Style`,
`spinner.Style`, progress options), see `references/theming.md`.

## Component catalog

| Import (`charm.land/bubbles/v2/…`) | Component | Use |
|---|---|---|
| `textinput` | single-line input | forms, search box |
| `textarea` | multi-line input | editors, comments |
| `list` | interactive list | selectable/filterable menus |
| `table` | interactive table | tabular data with a cursor |
| `viewport` | scrollable pane | logs, long text, rendered markdown |
| `spinner` | loading spinner | in-flight indicator |
| `progress` | progress bar | determinate progress |
| `paginator` | pagination state+dots | paged content |
| `help` | keybinding help | auto help bar from a KeyMap |
| `key` | keybinding definitions | declarative keys + help text |
| `timer` / `stopwatch` | countdown / count-up | timeouts, elapsed time |
| `filepicker` | file browser | pick a file/dir |

## The embedding pattern

```go
type model struct{ input textinput.Model }

func initial() model {
	ti := textinput.New()
	ti.Placeholder = "search…"
	ti.CharLimit = 64
	ti.SetWidth(30)
	ti.Focus() // must focus an input to receive keys
	return model{input: ti}
}

func (m model) Init() tea.Cmd { return textinput.Blink } // blinking cursor

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	if k, ok := msg.(tea.KeyPressMsg); ok && k.String() == "enter" {
		submit(m.input.Value()) // read value
	}
	var cmd tea.Cmd
	m.input, cmd = m.input.Update(msg) // always forward for cursor/typing
	return m, cmd
}

func (m model) View() tea.View { return tea.NewView(m.input.View()) }
```

## spinner

```go
s := spinner.New()
s.Spinner = spinner.Dot // Line, Dot, MiniDot, Jump, Points, Globe, Moon, Monkey…
s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("205"))
// Init returns s.Tick; in Update forward the msg: m.spinner, cmd = m.spinner.Update(msg)
```

## progress

```go
p := progress.New(progress.WithDefaultBlend()) // or WithColors(a, b) / WithColorFunc(fn)
// Static: render at a ratio.
p.ViewAs(0.62)
// Animated: SetPercent returns a Cmd; handle progress.FrameMsg by forwarding to p.Update,
// which returns the updated model and the next frame Cmd.
cmd := p.SetPercent(0.62)
```

## list

```go
items := []list.Item{item{title: "A"}, item{title: "B"}} // item implements list.Item
l := list.New(items, list.NewDefaultDelegate(), width, height)
l.Title = "Choose"
l.SetShowStatusBar(false)
// Update: m.list, cmd = m.list.Update(msg)
// Selection: sel, ok := m.list.SelectedItem().(item)
```

`list.Item` requires `FilterValue() string`. The default delegate expects items to also
implement `Title() string` and `Description() string`. Size the list from `WindowSizeMsg` via
`l.SetSize(w, h)`.

## table

```go
t := table.New(
	table.WithColumns([]table.Column{{Title: "Name", Width: 12}, {Title: "Age", Width: 4}}),
	table.WithRows([]table.Row{{"Ada", "36"}, {"Alan", "41"}}),
	table.WithFocused(true),
	table.WithHeight(8),
)
// Update: m.table, cmd = m.table.Update(msg)
// Cursor row: m.table.SelectedRow() // table.Row ([]string)
```

## viewport

Scrollable region for long/rendered content (pair with Glamour — see `glamour.md`):

```go
vp := viewport.New()
vp.SetWidth(80)
vp.SetHeight(20)
vp.SetContent(longText)
vp.Style = lipgloss.NewStyle().Border(lipgloss.RoundedBorder())
// Update: m.vp, cmd = m.vp.Update(msg) // handles ↑/↓, pgup/pgdn, mouse wheel
// Resize on tea.WindowSizeMsg with vp.SetWidth/SetHeight.
```

## key + help — declarative bindings

```go
import ("charm.land/bubbles/v2/key"; "charm.land/bubbles/v2/help")

type keyMap struct{ Up, Down, Quit key.Binding }

var keys = keyMap{
	Up:   key.NewBinding(key.WithKeys("up", "k"), key.WithHelp("↑/k", "up")),
	Down: key.NewBinding(key.WithKeys("down", "j"), key.WithHelp("↓/j", "down")),
	Quit: key.NewBinding(key.WithKeys("q", "ctrl+c"), key.WithHelp("q", "quit")),
}

// Match in Update — key.Matches needs a concrete fmt.Stringer, so assert the key msg first:
if k, ok := msg.(tea.KeyPressMsg); ok && key.Matches(k, keys.Quit) { return m, tea.Quit }

// Render a help bar. keyMap must implement help.KeyMap (ShortHelp/FullHelp).
h := help.New()
bar := h.View(keys)
```

`key.Matches(keyMsg, binding)` is the idiomatic way to test keys — cleaner than string
switches and it powers the auto-generated help. Toggle a binding with `binding.SetEnabled(false)`
to grey it out of help when unavailable.

## timer / stopwatch

`timer.New(timeout)` counts down and emits `timer.TickMsg` / `timer.TimeoutMsg`;
`stopwatch.New()` counts up. Both follow the forward-in-`Update` pattern and expose `.View()`.
