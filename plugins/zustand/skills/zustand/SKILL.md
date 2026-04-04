---
name: zustand
description: Zustand state management for React applications. This skill should be used when creating Zustand stores, implementing TypeScript store patterns, using middleware (persist, devtools, immer, subscribeWithSelector), building slice patterns for large stores, optimizing React component re-renders with selectors, implementing async actions and data fetching, or testing Zustand stores.
---

# Zustand State Management

Zustand is a small, fast, scalable state management solution for React. This skill covers store creation, TypeScript patterns, middleware, and performance optimization.

## Core Concepts

### Basic Store Creation

```typescript
import { create } from 'zustand'

interface BearStore {
  bears: number
  increase: () => void
  reset: () => void
}

const useBearStore = create<BearStore>((set) => ({
  bears: 0,
  increase: () => set((state) => ({ bears: state.bears + 1 })),
  reset: () => set({ bears: 0 }),
}))
```

### Using in Components

```typescript
// Select specific state (prevents unnecessary re-renders)
const bears = useBearStore((state) => state.bears)
const increase = useBearStore((state) => state.increase)

// Multiple selectors - use useShallow for object selections
import { useShallow } from 'zustand/react/shallow'
const { bears, increase } = useBearStore(
  useShallow((state) => ({ bears: state.bears, increase: state.increase }))
)
```

## References

For detailed patterns and advanced usage, load the appropriate reference:

| Topic | Reference | Use When |
|-------|-----------|----------|
| Store patterns | `references/store-patterns.md` | Creating stores, TypeScript setup, slice pattern, combining stores |
| Middleware | `references/middleware.md` | persist, devtools, immer, subscribeWithSelector, custom middleware |
| React integration | `references/react-integration.md` | Selectors, avoiding re-renders, subscriptions, context usage |
| Async & testing | `references/async-testing.md` | Async actions, data fetching, loading states, testing patterns |

## Quick Patterns

### Accessing State Outside React

```typescript
// Get current state
const bears = useBearStore.getState().bears

// Subscribe to changes
const unsub = useBearStore.subscribe((state) => console.log(state.bears))

// Update state
useBearStore.setState({ bears: 10 })
```

### Common Middleware Stack

```typescript
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

const useStore = create<Store>()(
  devtools(
    persist(
      immer((set) => ({
        // state and actions
      })),
      { name: 'store-key' }
    )
  )
)
```

## When to Load References

- **Creating a new store**: Load `store-patterns.md` for TypeScript setup and organization
- **Adding persistence/devtools**: Load `middleware.md` for middleware configuration
- **Performance issues**: Load `react-integration.md` for selector optimization
- **Async data fetching**: Load `async-testing.md` for async patterns and loading states
- **Writing tests**: Load `async-testing.md` for testing patterns
