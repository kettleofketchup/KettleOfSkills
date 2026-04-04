# Zustand Middleware

## Middleware Composition

Middleware wraps the store creator. Order matters - outer middleware runs first.

```typescript
import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// TypeScript: use create<Type>()() pattern for middleware
const useStore = create<Store>()(
  devtools(           // outer - wraps everything
    persist(          // middle
      immer(          // inner - closest to state
        (set) => ({ /* state */ })
      ),
      { name: 'store' }
    )
  )
)
```

## persist - Local Storage Persistence

```typescript
import { persist, createJSONStorage } from 'zustand/middleware'

const useStore = create<Store>()(
  persist(
    (set) => ({
      user: null,
      theme: 'light',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'app-storage',  // localStorage key

      // Optional: custom storage (default: localStorage)
      storage: createJSONStorage(() => sessionStorage),

      // Optional: only persist specific fields
      partialize: (state) => ({ theme: state.theme }),

      // Optional: migration between versions
      version: 1,
      migrate: (persisted, version) => {
        if (version === 0) {
          // migrate from v0 to v1
          return { ...persisted, newField: 'default' }
        }
        return persisted
      },

      // Optional: merge strategy for hydration
      merge: (persisted, current) => ({
        ...current,
        ...persisted,
      }),
    }
  )
)
```

### Hydration Handling

```typescript
// Check if store has been hydrated from storage
const useStore = create<Store>()(
  persist(
    (set) => ({ /* ... */ }),
    {
      name: 'store',
      onRehydrateStorage: () => (state, error) => {
        if (error) console.error('Hydration failed:', error)
        else console.log('Hydration complete')
      },
    }
  )
)

// Or use the hydration API
const { hasHydrated } = useStore.persist
useStore.persist.onFinishHydration(() => console.log('done'))
```

## devtools - Redux DevTools Integration

```typescript
import { devtools } from 'zustand/middleware'

const useStore = create<Store>()(
  devtools(
    (set) => ({
      count: 0,
      // Name actions for better DevTools experience
      increment: () => set(
        (s) => ({ count: s.count + 1 }),
        false,  // replace (false = merge)
        'increment'  // action name in DevTools
      ),
    }),
    {
      name: 'MyStore',  // store name in DevTools
      enabled: process.env.NODE_ENV === 'development',
    }
  )
)
```

## immer - Immutable Updates with Mutable Syntax

```typescript
import { immer } from 'zustand/middleware/immer'

const useStore = create<Store>()(
  immer((set) => ({
    users: [],
    updateUser: (id, name) => set((state) => {
      // Mutate directly - immer handles immutability
      const user = state.users.find(u => u.id === id)
      if (user) user.name = name
    }),
    addUser: (user) => set((state) => {
      state.users.push(user)
    }),
  }))
)
```

## subscribeWithSelector - Granular Subscriptions

Subscribe to specific state slices outside React.

```typescript
import { subscribeWithSelector } from 'zustand/middleware'

const useStore = create<Store>()(
  subscribeWithSelector((set) => ({
    count: 0,
    name: '',
    increment: () => set((s) => ({ count: s.count + 1 })),
  }))
)

// Subscribe to specific slice
const unsub = useStore.subscribe(
  (state) => state.count,           // selector
  (count, prevCount) => {           // listener
    console.log('Count changed:', prevCount, '->', count)
  },
  {
    equalityFn: Object.is,          // optional: custom equality
    fireImmediately: true,          // optional: fire on subscribe
  }
)
```

### Derived State Subscriptions

```typescript
// React to computed values
useStore.subscribe(
  (state) => state.items.filter(i => i.done).length,
  (doneCount) => console.log('Done items:', doneCount)
)
```

## combine - Auto-Infer State Type (Alternative to Manual Types)

```typescript
import { combine } from 'zustand/middleware'

// State type inferred from first arg, actions from second
const useStore = create(
  combine(
    { count: 0, name: '' },  // initial state (type inferred)
    (set) => ({              // actions
      increment: () => set((s) => ({ count: s.count + 1 })),
    })
  )
)
```

## Custom Middleware

```typescript
import { StateCreator, StoreMutatorIdentifier } from 'zustand'

type Logger = <
  T,
  Mps extends [StoreMutatorIdentifier, unknown][] = [],
  Mcs extends [StoreMutatorIdentifier, unknown][] = []
>(
  f: StateCreator<T, Mps, Mcs>,
  name?: string
) => StateCreator<T, Mps, Mcs>

const logger: Logger = (f, name) => (set, get, store) => {
  const loggedSet: typeof set = (...args) => {
    const prev = get()
    set(...args)
    console.log(name || 'store', { prev, next: get() })
  }
  return f(loggedSet, get, store)
}

// Usage
const useStore = create<Store>()(
  logger(
    (set) => ({ count: 0 }),
    'CounterStore'
  )
)
```

## Common Middleware Stacks

### Basic App Store

```typescript
create<Store>()(
  devtools(
    persist(
      (set) => ({ /* state */ }),
      { name: 'app' }
    )
  )
)
```

### Complex State with Nested Updates

```typescript
create<Store>()(
  devtools(
    persist(
      immer((set) => ({ /* state */ })),
      { name: 'app' }
    )
  )
)
```

### With External Subscriptions

```typescript
create<Store>()(
  devtools(
    subscribeWithSelector(
      persist(
        (set) => ({ /* state */ }),
        { name: 'app' }
      )
    )
  )
)
```
