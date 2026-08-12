---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Advanced Features: Misc

## Mouse Button Handling

Handle forward/back mouse buttons (mouse4/mouse5):

```go
// In options:
EnableDefaultContextMenu: false,
OnMouseDown: func(button int) {
    switch button {
    case 3: // back
        runtime.EventsEmit(app.ctx, "navigate:back")
    case 4: // forward
        runtime.EventsEmit(app.ctx, "navigate:forward")
    }
},
```

## Obfuscated Builds

Use [garble](https://github.com/burrowers/garble) to obfuscate Go binary:

```bash
wails build -obfuscated
```

Requires garble installed: `go install mvdan.cc/garble@latest`

Obfuscates Go symbols, strings, and package paths. Does NOT obfuscate frontend code (use frontend bundler minification for that).

## Overscroll Prevention

Prevent rubber-band/bounce scrolling on macOS and overscroll glow on Windows:

```css
html, body {
    overflow: hidden;
    height: 100%;
}

/* Or target specific containers */
.app-container {
    overflow: auto;
    overscroll-behavior: none;
}
```

`overscroll-behavior: none` prevents pull-to-refresh and bounce effects while allowing normal scroll within containers.
