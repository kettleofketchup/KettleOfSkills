# Shared theming — one palette, every widget

Define colors **once** and feed them into Lip Gloss, every Bubbles component, and Glamour. The
single source of truth is one background probe → one `lipgloss.LightDark` chooser built at
startup; never call `HasDarkBackground` per frame. See `lipgloss.md` for the color API.

## The Theme struct

```go
package theme

import (
	"image/color"
	"os"

	"charm.land/lipgloss/v2"
)

// Theme is the single source of truth for the app's colors. Build it ONCE at
// startup, then hand its fields/methods to every component.
type Theme struct {
	IsDark    bool
	LightDark lipgloss.LightDarkFunc          // the ONE adaptive chooser
	Fg, Muted, Accent, Border, Bg color.Color // text, dim, selection, frame, panel
}

func New() Theme {
	dark := lipgloss.HasDarkBackground(os.Stdin, os.Stdout) // one probe, at startup
	ld := lipgloss.LightDark(dark)
	return Theme{
		IsDark: dark, LightDark: ld,
		Fg:     ld(lipgloss.Color("#1A1A1A"), lipgloss.Color("#EEEEEE")), // light, dark
		Muted:  ld(lipgloss.Color("#6C6C6C"), lipgloss.Color("#9A9A9A")),
		Accent: ld(lipgloss.Color("#7D56F4"), lipgloss.Color("#B39DFF")),
		Border: ld(lipgloss.Color("#D0D0D0"), lipgloss.Color("#3A3A3A")),
		Bg:     ld(lipgloss.Color("#FFFFFF"), lipgloss.Color("#1A1A1A")),
	}
}

// Derive shades from seeds instead of hardcoding more colors.
func (t Theme) Hover() color.Color { return lipgloss.Lighten(t.Accent, 0.2) }

// hex picks a light/dark hex string for Glamour (whose color fields are *string).
func (t Theme) hex(light, dark string) *string {
	if t.IsDark {
		return &dark
	}
	return &light
}
```

## Lip Gloss base styles & borders

Expose shared styles as methods so every view builds from the same palette:

```go
func (t Theme) Base() lipgloss.Style  { return lipgloss.NewStyle().Foreground(t.Fg) }
func (t Theme) Title() lipgloss.Style { return lipgloss.NewStyle().Bold(true).Foreground(t.Accent) }
func (t Theme) Box() lipgloss.Style { // swap BorderForeground(t.Accent) to mark focus
	return lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).BorderForeground(t.Border).Padding(0, 1)
}
```

## Bubbles components — drive them all from `th := theme.New()`

```go
// list default delegate: NewDefaultDelegate hardcodes DARK — reset from IsDark, then override.
d := list.NewDefaultDelegate()
d.Styles = list.NewDefaultItemStyles(th.IsDark)
d.Styles.SelectedTitle = d.Styles.SelectedTitle.Foreground(th.Accent).BorderForeground(th.Accent)
d.Styles.NormalTitle   = d.Styles.NormalTitle.Foreground(th.Fg)
d.Styles.DimmedTitle   = d.Styles.DimmedTitle.Foreground(th.Muted)
l := list.New(items, d, w, h)
l.Styles = list.DefaultStyles(th.IsDark) // list chrome (title bar, status bar, pagination)
l.Styles.Title = l.Styles.Title.Background(th.Accent).Foreground(th.Bg)

// table — Header / Cell / Selected
ts := table.DefaultStyles()
ts.Header   = ts.Header.Foreground(th.Muted).BorderForeground(th.Border).Bold(true)
ts.Selected = ts.Selected.Foreground(th.Bg).Background(th.Accent)
tbl := table.New(table.WithColumns(cols), table.WithStyles(ts)) // or tbl.SetStyles(ts)

// textinput — the styles field is UNEXPORTED in v2: use the Styles()/SetStyles() pair
ti := textinput.New()
tis := ti.Styles()
tis.Focused.Prompt      = tis.Focused.Prompt.Foreground(th.Accent)
tis.Focused.Text        = tis.Focused.Text.Foreground(th.Fg)
tis.Focused.Placeholder = tis.Focused.Placeholder.Foreground(th.Muted)
tis.Cursor.Color        = th.Accent // CursorStyle.Color (color.Color)
ti.SetStyles(tis)

// help — ShortKey / ShortDesc / FullKey / FullDesc
hp := help.New()
hp.Styles = help.DefaultStyles(th.IsDark)
hp.Styles.ShortKey  = hp.Styles.ShortKey.Foreground(th.Accent)
hp.Styles.ShortDesc = hp.Styles.ShortDesc.Foreground(th.Muted)

vp := viewport.New()
vp.Style = th.Box()                                                       // viewport frame
sp := spinner.New(spinner.WithStyle(lipgloss.NewStyle().Foreground(th.Accent))) // or sp.Style = …
pr := progress.New(progress.WithColors(th.Accent, th.Hover()))           // 2+ colors ⇒ blended bar
```

## Glamour markdown

Clone a prebuilt `ansi.StyleConfig` for the theme's mode, overwrite the color fields (they are
`*string` hex/ANSI), then inject with `WithStyles`:

```go
import ("charm.land/glamour/v2"; "charm.land/glamour/v2/styles")

cfg := styles.LightStyleConfig
if th.IsDark {
	cfg = styles.DarkStyleConfig
}
cfg.Document.Color = th.hex("#1A1A1A", "#EEEEEE")
cfg.H1.Color       = th.hex("#7D56F4", "#B39DFF") // accent
cfg.Link.Color     = th.hex("#7D56F4", "#B39DFF")
r, _ := glamour.NewTermRenderer(glamour.WithStyles(cfg), glamour.WithWordWrap(78))
```

The viewport frame around rendered markdown is themed separately via `vp.Style = th.Box()`.
(`WithAutoStyle` does not exist in v2 — pick the config from `th.IsDark`; see `glamour.md`.)

## Lip Gloss `table` / `list` static renderers

```go
t := table.New(). // import charm.land/lipgloss/v2/table
	BorderStyle(lipgloss.NewStyle().Foreground(th.Border)).
	StyleFunc(func(row, col int) lipgloss.Style {
		if row == table.HeaderRow {
			return th.Title().Padding(0, 1)
		}
		return th.Base().Padding(0, 1)
	})
lst := list.New("Apples", "Oranges"). // import charm.land/lipgloss/v2/list
	EnumeratorStyle(lipgloss.NewStyle().Foreground(th.Accent).MarginRight(1)).
	ItemStyle(th.Base())
```

One `theme.New()` value now drives Bubble Tea (`tea.View.BackgroundColor = th.Bg`), every
Bubbles widget, Glamour, and both static renderers — change a seed in one place, it propagates.
BubbleZone and Harmonica have no color knobs; style their content with these same theme styles.
