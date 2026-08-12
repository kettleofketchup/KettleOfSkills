---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Frontend Integration

## Any Framework Works

Wails frontend is standard web tech. Templates: `svelte`, `react`, `vue`, `preact`, `lit`, `vanilla` (each with `-ts` variant). Frontend lives in `frontend/`. Wails runs framework's dev server in dev mode, embeds build output for production.

## Calling Bound Go from JS

Import generated bindings from `wailsjs/go/` directory:

```js
import { Greet } from '../wailsjs/go/main/App';

// All bound methods return Promises
const result = await Greet("World");
```

Import generated models:

```js
import { Person } from '../wailsjs/go/models';
const p = Person.createFrom(data);
```

## Wails JS Runtime

```js
import * as runtime from '../wailsjs/runtime/runtime';

// Window operations
runtime.WindowSetTitle("New Title");
runtime.WindowFullscreen();
runtime.WindowMinimise();
runtime.WindowMaximise();
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
runtime.EventsOn("myEvent", (data) => { console.log(data); });
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

`wailsjs/go/` is regenerated on each `wails dev`/`wails build`/`wails generate module`. `wailsjs/runtime/` is static.

## Custom Templates

Use any git repo as template:

```bash
wails init -n myapp -t https://github.com/user/my-wails-template
```

Template requires: `frontend/` with package.json, `main.go`, `wails.json`, `go.mod`. Set `"frontend:dev:serverUrl": "auto"` for Vite auto-detection.
