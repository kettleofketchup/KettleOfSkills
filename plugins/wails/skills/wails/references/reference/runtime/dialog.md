---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference/runtime
---

# Dialog Runtime API

Native OS dialogs for file selection and messages. All Go functions take `ctx context.Context` as first parameter.

## File Dialogs

### Go Signatures

```go
func OpenFileDialog(ctx context.Context, opts OpenDialogOptions) (string, error)
func OpenMultipleFilesDialog(ctx context.Context, opts OpenDialogOptions) ([]string, error)
func SaveFileDialog(ctx context.Context, opts SaveDialogOptions) (string, error)
```

### OpenDialogOptions / SaveDialogOptions

| Field | Type | Description |
|---|---|---|
| `DefaultDirectory` | `string` | Directory to open dialog in |
| `DefaultFilename` | `string` | Default filename |
| `Title` | `string` | Dialog title |
| `Filters` | `[]FileFilter` | File type filters |
| `ShowHiddenFiles` | `bool` | Show hidden files (Linux/macOS) |
| `CanCreateDirectories` | `bool` | Allow creating directories (macOS) |
| `ResolvesAliases` | `bool` | Resolve aliases to targets (macOS) |
| `TreatPackagesAsDirectories` | `bool` | Navigate into .app bundles (macOS) |

### FileFilter

```go
type FileFilter struct {
    DisplayName string  // e.g. "Image Files (*.jpg, *.png)"
    Pattern     string  // e.g. "*.jpg;*.png"
}
```

Pattern uses semicolons to separate multiple extensions.

## Message Dialog

### Go Signature

```go
func MessageDialog(ctx context.Context, opts MessageDialogOptions) (string, error)
```

Returns the label of the button that was clicked.

### MessageDialogOptions

| Field | Type | Description |
|---|---|---|
| `Type` | `DialogType` | Dialog icon/type |
| `Title` | `string` | Dialog title |
| `Message` | `string` | Dialog message body |
| `Buttons` | `[]string` | Button labels |
| `DefaultButton` | `string` | Default (focused) button label |
| `CancelButton` | `string` | Button triggered by Escape |
| `Icon` | `[]byte` | Custom icon (PNG/JPEG bytes) |

### DialogType Constants

| Constant | Value | Description |
|---|---|---|
| `InfoDialog` | — | Information icon |
| `ErrorDialog` | — | Error icon |
| `QuestionDialog` | — | Question icon |
| `WarningDialog` | — | Warning icon |

## JS Equivalents

All available via `window.runtime`:

```js
// File dialogs
let path = await window.runtime.OpenFileDialog(options);
let paths = await window.runtime.OpenMultipleFilesDialog(options);
let savePath = await window.runtime.SaveFileDialog(options);

// Message dialog
let clicked = await window.runtime.MessageDialog(options);
```

JS options objects mirror Go structs (camelCase field names).

## Usage Example (Go)

```go
selection, err := runtime.OpenFileDialog(ctx, runtime.OpenDialogOptions{
    Title: "Select Config File",
    DefaultDirectory: "/etc",
    Filters: []runtime.FileFilter{
        {DisplayName: "YAML Files", Pattern: "*.yml;*.yaml"},
        {DisplayName: "All Files", Pattern: "*"},
    },
})

result, err := runtime.MessageDialog(ctx, runtime.MessageDialogOptions{
    Type:          runtime.QuestionDialog,
    Title:         "Confirm",
    Message:       "Delete this item?",
    Buttons:       []string{"Yes", "No"},
    DefaultButton: "No",
    CancelButton:  "No",
})
if result == "Yes" {
    // delete
}
```
