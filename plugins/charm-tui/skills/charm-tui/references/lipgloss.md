# Lip Gloss — styling and layout

Module: `charm.land/lipgloss/v2`. Declarative, chainable styling for terminal strings, plus
layout helpers and `table`/`list`/`tree` sub-renderers. Styles are immutable value types:
chaining returns a copy, so styles are safe to share and reuse.

## Styles

```go
style := lipgloss.NewStyle().
	Bold(true).Italic(true).Underline(true).Faint(true).Reverse(true).
	Foreground(lipgloss.Color("#FAFAFA")).
	Background(lipgloss.Color("#7D56F4")).
	Padding(1, 2).            // vertical, horizontal (also Padding(t,r,b,l))
	Margin(1).
	Width(24).Height(3).
	Align(lipgloss.Center)    // Left | Center | Right

out := style.Render("Hello, TUI")
lipgloss.Println(out)         // use lipgloss.Print* — downsamples color to the terminal
```

`SetString("text")` bakes text into the style so `Render()` takes no args. `Inherit(other)`
copies only unset rules from `other`. `UnsetBold()` etc. clear a rule.

## Colors (v2)

`lipgloss.Color(string)` covers every profile by the string form:

- `lipgloss.Color("5")` — ANSI 16 (0–15)
- `lipgloss.Color("86")` — ANSI 256 (16–255)
- `lipgloss.Color("#7D56F4")` — 24-bit truecolor hex

Named constants exist: `lipgloss.Red`, `lipgloss.BrightBlue`, `lipgloss.Black`, etc.

**Light/dark adaptation** (replaces v1 `AdaptiveColor`). Detect the background once, build a
chooser, reuse it:

```go
hasDark := lipgloss.HasDarkBackground(os.Stdin, os.Stdout)
lightDark := lipgloss.LightDark(hasDark)
fg := lightDark(lipgloss.Color("#0A0A0A"), lipgloss.Color("#FAFAFA")) // light choice, dark choice
```

Color math: `lipgloss.Lighten(c, 0.3)`, `lipgloss.Darken(c, 0.5)`, `lipgloss.Alpha(c, 0.2)`,
`lipgloss.Blend1D(steps, a, b)` for gradients. Build these into one shared chooser and derive a
whole palette from a few seeds — see `references/theming.md`.

## Borders

```go
lipgloss.NewStyle().
	Border(lipgloss.RoundedBorder()).           // Normal|Rounded|Thick|Double|Hidden|ASCII|Markdown
	BorderForeground(lipgloss.Color("62")).
	Border(lipgloss.ThickBorder(), true, false) // (style, top&bottom, left&right) to pick sides
```

`GetHorizontalFrameSize()` / `GetVerticalFrameSize()` return the total border+padding+margin a
style adds — subtract these when sizing inner content (e.g. a viewport inside a bordered box).

## Layout

```go
// Join blocks. Second+ args are the blocks; first arg is cross-axis alignment.
lipgloss.JoinHorizontal(lipgloss.Top, left, right)    // side by side
lipgloss.JoinVertical(lipgloss.Left, header, body)    // stacked
lipgloss.JoinHorizontal(0.2, a, b)                    // align 20% from top

// Place a block within a larger cell (great with WindowSizeMsg dimensions).
lipgloss.Place(width, height, lipgloss.Center, lipgloss.Center, block)
lipgloss.PlaceHorizontal(width, lipgloss.Right, block)

// Measure rendered blocks (accounts for ANSI + wide runes).
w := lipgloss.Width(block)
h := lipgloss.Height(block)
w, h = lipgloss.Size(block)
```

Center a box on a full-screen app using the `tea.WindowSizeMsg` dimensions:

```go
box := lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).Padding(1, 3).Render(content)
view := lipgloss.Place(m.width, m.height, lipgloss.Center, lipgloss.Center, box)
```

## Tables — `charm.land/lipgloss/v2/table`

```go
import "charm.land/lipgloss/v2/table"

t := table.New().
	Border(lipgloss.NormalBorder()).
	Headers("LANG", "FORMAL", "INFORMAL").
	Row("Chinese", "您好", "你好").
	Rows(moreRows...). // moreRows is [][]string
	StyleFunc(func(row, col int) lipgloss.Style {
		if row == table.HeaderRow {
			return lipgloss.NewStyle().Bold(true).Padding(0, 1)
		}
		return lipgloss.NewStyle().Padding(0, 1)
	})
lipgloss.Println(t) // t stringifies
```

`table.HeaderRow` is the sentinel row index for headers in `StyleFunc`. Use `Width(n)` to fix
total table width and wrap cells.

## Lists — `charm.land/lipgloss/v2/list`

```go
import "charm.land/lipgloss/v2/list"

l := list.New("Apples", "Oranges", "Pears").
	Enumerator(list.Roman).        // Arabic | Alphabet | Roman | Bullet | Dash | custom
	EnumeratorStyle(lipgloss.NewStyle().Foreground(lipgloss.Color("99")).MarginRight(1))
```

Nest by passing a `list.New(...)` as an item. This `list` is a **static renderer** — for an
interactive, navigable/filterable list use the Bubbles `list` component instead.

## Trees — `charm.land/lipgloss/v2/tree`

```go
import "charm.land/lipgloss/v2/tree"

t := tree.Root(".").Child("cmd", tree.New().Root("internal").Child("app", "db"))
lipgloss.Println(t)
```

## table vs list: static vs interactive

Lip Gloss `table`/`list`/`tree` render a snapshot. When you need selection, scrolling, or
filtering, reach for the Bubbles `table`/`list`/`viewport` components (see `bubbles.md`).
