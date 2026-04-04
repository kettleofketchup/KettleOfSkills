---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Frontend Integration

## Any Framework Works

Wails frontend is standard web tech. Use any framework:
- **Svelte** (default template)
- **React** (template: `-t react-ts`)
- **Vue** (template: `-t vue-ts`)
- **Preact** (template: `-t preact-ts`)
- **Lit** (template: `-t lit-ts`)
- **Vanilla** (template: `-t vanilla-ts`)

Frontend lives in `frontend/` directory. Wails runs framework's dev server in dev mode, embeds build output for production.

## Calling Bound Go from JS

Import generated bindings from `wailsjs/go/` directory:

```js
// Package path mirrors Go package structure
import { Greet } from '../wailsjs/go/main/App';

// All bound methods return Promises
const result = await Greet("World");
```

Multiple bound structs each get their own file:

```js
import { GetUser } from '../wailsjs/go/main/UserService';
import { SaveConfig } from '../wailsjs/go/main/ConfigService';
```

Import generated models:

```js
import { Person } from '../wailsjs/go/models';
const p = Person.createFrom(data);
```

## Wails JS Runtime

Runtime available at `window.runtime` or via import:

```js
import * as runtime from '../wailsjs/runtime/runtime';

// Window operations
runtime.WindowSetTitle("New Title");
runtime.WindowFullscreen();
runtime.WindowMinimise();
runtime.WindowMaximise();
runtime.WindowUnmaximise();
runtime.WindowCenter();
runtime.WindowSetSize(800, 600);
runtime.WindowSetPosition(100, 100);
runtime.WindowShow();
runtime.WindowHide();

// Dialogs
const file = await runtime.OpenFileDialog({ title: "Open File" });
const dir = await runtime.OpenDirectoryDialog({ title: "Select Folder" });
const save = await runtime.SaveFileDialog({ title: "Save As" });

// Events
runtime.EventsOn("myEvent", (data) => {
    console.log(data);
});
runtime.EventsOnce("oneTimeEvent", callback);
runtime.EventsEmit("eventName", data);
runtime.EventsOff("myEvent");

// System
runtime.BrowserOpenURL("https://example.com");
runtime.ClipboardGetText();
runtime.ClipboardSetText("copied");
runtime.Environment(); // returns OS, arch, etc.

// Logging
runtime.LogDebug("debug msg");
runtime.LogInfo("info msg");
runtime.LogWarning("warn msg");
runtime.LogError("error msg");

// Menu
runtime.MenuSetApplicationMenu(menuJSON);
runtime.MenuUpdateApplicationMenu();
```

## Generated Files Structure

```
frontend/wailsjs/
├── go/                    # Generated Go bindings
│   ├── main/              # Package name = directory
│   │   ├── App.js         # JS wrapper functions
│   │   └── App.d.ts       # TypeScript declarations
│   └── models.ts          # All struct type definitions
└── runtime/               # Wails runtime
    ├── runtime.js         # Runtime functions
    └── runtime.d.ts       # Runtime type declarations
```

- `wailsjs/go/` - regenerated on each `wails dev`/`wails build`/`wails generate module`
- `wailsjs/runtime/` - static, ships with Wails

## Template Frameworks

Built-in templates:

```bash
wails init -n myapp -t svelte-ts     # Svelte + TypeScript
wails init -n myapp -t react-ts      # React + TypeScript
wails init -n myapp -t vue-ts        # Vue + TypeScript
wails init -n myapp -t preact-ts     # Preact + TypeScript
wails init -n myapp -t lit-ts        # Lit + TypeScript
wails init -n myapp -t vanilla-ts    # Vanilla + TypeScript
wails init -n myapp -t svelte        # Svelte (no TS)
wails init -n myapp -t react         # React (no TS)
wails init -n myapp -t vue           # Vue (no TS)
```

### Custom Templates

Use any git repo as template:

```bash
wails init -n myapp -t https://github.com/user/my-wails-template
```

Template structure requires:
- `frontend/` directory with package.json
- `main.go` at root
- `wails.json` config
- `go.mod`

`wails.json` specifies frontend build/install commands:

```json
{
  "name": "myapp",
  "frontend:install": "npm install",
  "frontend:build": "npm run build",
  "frontend:dev:watcher": "npm run dev",
  "frontend:dev:serverUrl": "auto"
}
```

`frontend:dev:serverUrl: "auto"` auto-detects the Vite dev server URL.
