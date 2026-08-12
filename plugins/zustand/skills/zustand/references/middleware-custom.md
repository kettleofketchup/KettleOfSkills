# Zustand Custom Middleware & Stacks

Split out of `middleware.md`; see it for the preceding sections.

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
