---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference
---

# Menus: Full Example & Dynamic Updates

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

## Dynamic Menu Updates

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

Must call `appMenu.Update()` after modifying any menu item properties. Changes are not applied until `Update()` is called.

## Radio Groups

Consecutive Radio items form a mutually exclusive group:

```go
menu.Radio("Option A", true, nil, func(cd *menu.CallbackData) {
    // A selected, B and C deselected automatically
})
menu.Radio("Option B", false, nil, handler)
menu.Radio("Option C", false, nil, handler)
```

`cd.MenuItem.Checked` is `true` for the newly selected item.
