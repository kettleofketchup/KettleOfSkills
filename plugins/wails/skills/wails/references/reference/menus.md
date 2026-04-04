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
| Radio | `menu.Radio(label, selected, accelerator, callback)` | Mutually exclusive within group (consecutive radios form a group) |
| Submenu | `menu.SubMenu(label, subMenu)` | Nested menu; `subMenu` is a `*menu.Menu` |

### Callback signature

```go
func(cd *menu.CallbackData) {
    // cd.MenuItem - the menu item that triggered
    // For Checkbox: cd.MenuItem.Checked (toggled before callback)
    // For Radio: cd.MenuItem.Checked (set true, others in group set false)
}
```

## Menu Methods

| Method | Description |
|--------|-------------|
| `menu.Append(item)` | Add item to end of menu |
| `menu.Prepend(item)` | Add item to start of menu |
| `menu.Update()` | Re-render menu after dynamic changes |

## Roles (Predefined Menus)

Pre-built menus with platform-appropriate defaults.

| Role | Description |
|------|-------------|
| `menu.AppMenu()` | macOS standard app menu (About, Services, Hide, Quit) |
| `menu.EditMenu()` | Undo, Redo, Cut, Copy, Paste, Select All |
| `menu.FileMenu()` | Close window (macOS: Cmd+W) |
| `menu.ViewMenu()` | Reload, Toggle Fullscreen, Minimize, Zoom |
| `menu.WindowMenu()` | Minimize, Zoom |
| `menu.HelpMenu()` | (empty placeholder submenu) |

Role menu items (usable individually):

| Item | Description |
|------|-------------|
| `menu.QuitItem()` | Quit application |
| `menu.UndoItem()` | Undo |
| `menu.RedoItem()` | Redo |
| `menu.CutItem()` | Cut |
| `menu.CopyItem()` | Copy |
| `menu.PasteItem()` | Paste |
| `menu.SelectAllItem()` | Select all |
| `menu.MinimizeItem()` | Minimize window |
| `menu.ZoomItem()` | Zoom window |
| `menu.FullscreenItem()` | Toggle fullscreen |
| `menu.CloseItem()` | Close window |
| `menu.ReloadItem()` | Reload page |
| `menu.ForceReloadItem()` | Force reload (clear cache) |
| `menu.ToggleDevToolsItem()` | Toggle developer tools |

## Accelerators (Keyboard Shortcuts)

Construct with `keys.CmdOrCtrl(key)`, `keys.Combo(key, ...modifiers)`, etc.

| Modifier | Constant | Notes |
|----------|----------|-------|
| Cmd/Ctrl | `keys.CmdOrCtrlKey` | Cmd on macOS, Ctrl on Windows/Linux |
| Shift | `keys.ShiftKey` | |
| Alt/Option | `keys.OptionOrAltKey` | Option on macOS, Alt on Windows/Linux |
| Control | `keys.ControlKey` | Ctrl on all platforms |
| Super | `keys.SuperKey` | Win/Cmd key |

### Key constants

`keys.Key*` -- letters (`keys.KeyA` - `keys.KeyZ`), digits (`keys.Key0` - `keys.Key9`), function keys (`keys.KeyF1` - `keys.KeyF35`), special keys (`keys.KeyEscape`, `keys.KeyReturn`, `keys.KeyTab`, `keys.KeySpace`, `keys.KeyBackspace`, `keys.KeyDelete`, `keys.KeyInsert`, `keys.KeyHome`, `keys.KeyEnd`, `keys.KeyUp`, `keys.KeyDown`, `keys.KeyLeft`, `keys.KeyRight`, `keys.KeyPageUp`, `keys.KeyPageDown`)

### Examples

```go
// Cmd+S / Ctrl+S
keys.CmdOrCtrl("s")

// Cmd+Shift+S / Ctrl+Shift+S
keys.Combo("s", keys.CmdOrCtrlKey, keys.ShiftKey)

// Alt+F4
keys.Combo("F4", keys.OptionOrAltKey)

// Ctrl+Shift+I
keys.Combo("i", keys.ControlKey, keys.ShiftKey)
```

## Full Example

```go
appMenu := menu.NewMenu()

// macOS app menu
appMenu.Append(menu.AppMenu())

// File menu
fileMenu := appMenu.AddSubmenu("File")
fileMenu.Append(menu.Text("New", keys.CmdOrCtrl("n"), func(cd *menu.CallbackData) {
    // handle new
}))
fileMenu.Append(menu.Text("Open", keys.CmdOrCtrl("o"), func(cd *menu.CallbackData) {
    // handle open
}))
fileMenu.Append(menu.Separator())
fileMenu.Append(menu.Text("Save", keys.CmdOrCtrl("s"), func(cd *menu.CallbackData) {
    // handle save
}))
fileMenu.Append(menu.Separator())
fileMenu.Append(menu.QuitItem())

// Edit menu (standard role)
appMenu.Append(menu.EditMenu())

// View with checkbox
viewMenu := appMenu.AddSubmenu("View")
viewMenu.Append(menu.Checkbox("Dark Mode", false, keys.CmdOrCtrl("d"), func(cd *menu.CallbackData) {
    isDark := cd.MenuItem.Checked
    // toggle theme
}))
viewMenu.Append(menu.Separator())
viewMenu.Append(menu.FullscreenItem())

// Set on app
app := &options.App{
    Menu: appMenu,
}
```

### Dynamic menu updates

```go
// Store reference to menu item
var myItem *menu.MenuItem

myItem = menu.Text("Enabled", nil, nil)
myItem.Disabled = false

// Later, disable and re-render
myItem.Disabled = true
myItem.Label = "Disabled"
appMenu.Update()  // must call Update() to apply changes
```
