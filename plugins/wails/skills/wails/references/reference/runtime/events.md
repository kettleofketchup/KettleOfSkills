---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference/runtime
---

# Events Runtime API

Events enable communication between Go and JS. Events are **one-directional**: an event emitted in Go is received by JS listeners, and vice versa. Both sides can emit and listen independently.

## Go Functions

All take `ctx context.Context` as first parameter.

### Listening

```go
// Listen indefinitely. Returns cancel function.
func EventsOn(ctx context.Context, eventName string, callback func(optionalData ...interface{})) func()

// Listen for at most `counter` events. Returns cancel function.
func EventsOnMultiple(ctx context.Context, eventName string, callback func(optionalData ...interface{}), counter int) func()

// Listen for exactly one event. Returns cancel function.
func EventsOnce(ctx context.Context, eventName string, callback func(optionalData ...interface{})) func()
```

The returned `func()` can be called to cancel/unregister the listener.

### Emitting

```go
// Emit event with optional data (variadic)
func EventsEmit(ctx context.Context, eventName string, optionalData ...interface{})
```

### Removing Listeners

```go
// Remove listeners for given event name(s)
func EventsOff(ctx context.Context, eventName string, additionalEventNames ...string)
```

## JS Functions

All accessed via `window.runtime`.

| JS | Description |
|---|---|
| `EventsOn(eventName, callback)` | Listen indefinitely. Returns cancel fn. |
| `EventsOnce(eventName, callback)` | Listen once. Returns cancel fn. |
| `EventsOnMultiple(eventName, callback, maxCount)` | Listen N times. Returns cancel fn. |
| `EventsEmit(eventName, ...data)` | Emit event with optional data |
| `EventsOff(eventName, ...additionalNames)` | Remove listeners for event(s) |

## Event Direction

| Emitter | Listener | Flow |
|---|---|---|
| Go `EventsEmit` | JS `EventsOn` | Go -> JS |
| JS `EventsEmit` | Go `EventsOn` | JS -> Go |
| Go `EventsEmit` | Go `EventsOn` | Go -> Go (same process) |
| JS `EventsEmit` | JS `EventsOn` | JS -> JS (same process) |

## Usage Example

**Go (backend):**
```go
// Listen for frontend events
runtime.EventsOn(ctx, "user:login", func(data ...interface{}) {
    username := data[0].(string)
    log.Printf("User logged in: %s", username)
})

// Emit to frontend
runtime.EventsEmit(ctx, "data:updated", payload)
```

**JS (frontend):**
```js
// Listen for backend events
const cancel = window.runtime.EventsOn("data:updated", (payload) => {
    console.log("Data updated:", payload);
});

// Emit to backend
window.runtime.EventsEmit("user:login", "alice");

// Stop listening
cancel();
// Or: window.runtime.EventsOff("data:updated");
```
