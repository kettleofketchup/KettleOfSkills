---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference
---

# Native Menus

Wails supports native application menus (macOS menu bar, Windows/Linux window menus).

## Menu Struct

```go
import "github.com/wailsapp/wails/v2/pkg/menu"
import "github.com/wailsapp/wails/v2/pkg/menu/keys"

appMenu := menu.NewMenu()
```

Set via application option:
```go
app := &options.App{
    Menu: appMenu,
}
```

## MenuItem Types

| Type | Constructor | Description |
|------|-------------|-------------|
| Text | `menu.Text(label, accelerator, callback)` | Standard clickable item |
| Separator | `menu.Separator()` | Visual divider line |
| Checkbox | `menu.Checkbox(label, checked, accelerator, callback)` | Toggleable item |
| Radio | `menu.Radio(label, selected, accelerator, callback)` | Mutually exclusive within group |
| Submenu | `menu.SubMenu(label, subMenu)` | Nested menu |

Callback signature: `func(cd *menu.CallbackData)` where `cd.MenuItem` is the item that triggered.

## Roles (Predefined Menus)

| Role | Description |
|------|-------------|
| `menu.AppMenu()` | macOS standard app menu (About, Services, Hide, Quit) |
| `menu.EditMenu()` | Undo, Redo, Cut, Copy, Paste, Select All |
| `menu.FileMenu()` | Close window (macOS: Cmd+W) |
| `menu.ViewMenu()` | Reload, Toggle Fullscreen, Minimize, Zoom |
| `menu.WindowMenu()` | Minimize, Zoom |

Role items: `menu.QuitItem()`, `menu.UndoItem()`, `menu.RedoItem()`, `menu.CutItem()`, `menu.CopyItem()`, `menu.PasteItem()`, `menu.SelectAllItem()`, `menu.MinimizeItem()`, `menu.ZoomItem()`, `menu.FullscreenItem()`, `menu.CloseItem()`, `menu.ReloadItem()`, `menu.ToggleDevToolsItem()`

## Accelerators (Keyboard Shortcuts)

| Constructor | Notes |
|------------|-------|
| `keys.CmdOrCtrl("s")` | Cmd on macOS, Ctrl on Windows/Linux |
| `keys.Combo("s", keys.CmdOrCtrlKey, keys.ShiftKey)` | Multiple modifiers |
| `keys.Combo("F4", keys.OptionOrAltKey)` | Alt+F4 |

## Menu Methods

| Method | Description |
|--------|-------------|
| `menu.Append(item)` | Add item to end of menu |
| `menu.Prepend(item)` | Add item to start of menu |
| `menu.Update()` | Re-render menu after dynamic changes |

See [Menus: Full Example & Dynamic Updates](menus-example.md) for complete usage patterns.
