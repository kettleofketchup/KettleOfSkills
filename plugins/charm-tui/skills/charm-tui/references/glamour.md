# Glamour — Markdown in the terminal

Module: `charm.land/glamour/v2`. Renders Markdown (CommonMark + GFM) into styled ANSI. Great
for help screens, changelogs, docs viewers, and anything you already have as Markdown.

## One-shot render

```go
import "charm.land/glamour/v2"

out, err := glamour.Render(markdown, "dark") // returns the styled string
fmt.Print(out)
```

Built-in style names: `"dark"`, `"light"`, `"notty"` (no color), `"ascii"`, `"dracula"`,
`"pink"`, `"tokyo-night"`. `glamour.RenderWithEnvironmentConfig(md)` honors the `GLAMOUR_STYLE`
env var (a style name or a path to a JSON theme).

## Reusable renderer

Build a `TermRenderer` once when you need word-wrapping, a fixed style, or a fixed width.
Glamour v2 removed `WithAutoStyle` (the default is `"dark"`) — detect the background yourself:

```go
style := "dark" // glamour's default
if !lipgloss.HasDarkBackground(os.Stdin, os.Stdout) {
	style = "light"
}
r, err := glamour.NewTermRenderer(
	glamour.WithStandardStyle(style), // "dark" | "light" | "dracula" | "notty" | …
	glamour.WithWordWrap(80),         // wrap column (0 disables wrapping)
	glamour.WithEmoji(),              // render :emoji: shortcodes
)
if err != nil { /* handle */ }
out, err := r.Render(markdown)
```

To drive the `ansi.StyleConfig` colors from the same palette as your Lip Gloss/Bubbles styles,
see `references/theming.md`.

Other option constructors: `WithStandardStyle("dracula")`, `WithStylePath("./theme.json")`,
`WithStyles(styleConfig)` (a programmatic `ansi.StyleConfig`), `WithEnvironmentConfig()`,
`WithPreservedNewLines()`.

## Explicit style configs

For light/dark control tied to the terminal (as Bubble Tea apps do), import the style configs:

```go
import (
	"charm.land/glamour/v2"
	"charm.land/glamour/v2/styles"
	"charm.land/lipgloss/v2"
)

cfg := styles.DarkStyleConfig
if !lipgloss.HasDarkBackground(os.Stdin, os.Stdout) {
	cfg = styles.LightStyleConfig
}
r, _ := glamour.NewTermRenderer(glamour.WithStyles(cfg), glamour.WithWordWrap(78))
```

## Inside a Bubble Tea viewport (the common pattern)

Glamour produces static text; wrap it in a Bubbles `viewport` for scrolling. Render at a width
that subtracts the viewport's frame so lines don't overflow:

```go
vp := viewport.New()
vp.SetWidth(width)
vp.SetHeight(height)
vp.Style = lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).PaddingRight(2)

// Glamour adds a small left gutter; account for it plus the viewport frame.
const gutter = 3
renderWidth := width - vp.Style.GetHorizontalFrameSize() - gutter

style := "dark"
if !lipgloss.HasDarkBackground(os.Stdin, os.Stdout) { style = "light" }
r, _ := glamour.NewTermRenderer(glamour.WithStandardStyle(style), glamour.WithWordWrap(renderWidth))
md, _ := r.Render(content)
vp.SetContent(md)
// Forward key/mouse msgs to vp.Update for scrolling; render vp.View() in your model's View().
```

## Notes

- **Re-render on resize.** Word wrap is baked into the output string, so on a
  `tea.WindowSizeMsg` rebuild the renderer at the new width and call `vp.SetContent` again.
- Use `"notty"` when piping output to a file so no ANSI escapes leak. Glamour v2 is "pure" — it
  always emits the same output for a given style (no `WithAutoStyle`/profile auto-detection), so
  choose the style explicitly.
- Rendering is not free for large documents — render once and cache the string; don't re-render
  every frame in `View()`.
