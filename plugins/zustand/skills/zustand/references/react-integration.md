# Zustand React Integration

## Selectors and Re-renders

### The Golden Rule

Components re-render when their selected state changes. Select only what you need.

```typescript
// BAD - re-renders on ANY state change
const state = useStore()

// GOOD - re-renders only when count changes
const count = useStore((state) => state.count)

// GOOD - stable action reference (actions don't change)
const increment = useStore((state) => state.increment)
```

### Multiple Values with useShallow

```typescript
import { useShallow } from 'zustand/react/shallow'

// BAD - creates new object every render, causes infinite re-renders
const { count, name } = useStore((state) => ({ count: state.count, name: state.name }))

// GOOD - useShallow does shallow comparison
const { count, name } = useStore(
  useShallow((state) => ({ count: state.count, name: state.name }))
)

// GOOD - useShallow with array
const [count, name] = useStore(
  useShallow((state) => [state.count, state.name])
)
```

### Custom Equality Functions

```typescript
// Custom equality for specific comparison needs
const user = useStore(
  (state) => state.user,
  (a, b) => a?.id === b?.id  // only re-render if user.id changes
)
```

### Selector with Props

```typescript
// Create selector outside component to avoid recreation
const selectTodo = (id: string) => (state: State) =>
  state.todos.find(t => t.id === id)

function TodoItem({ id }: { id: string }) {
  const todo = useStore(selectTodo(id))
  // ...
}
```

## Subscription Patterns

### Subscribe Outside React

```typescript
// Global subscription (e.g., in a service, effect, or module)
const unsub = useStore.subscribe((state, prevState) => {
  if (state.user !== prevState.user) {
    analytics.identify(state.user)
  }
})

// With subscribeWithSelector middleware for granular subscriptions
const unsub = useStore.subscribe(
  (state) => state.user,
  (user) => analytics.identify(user)
)
```

### useEffect Subscription

```typescript
useEffect(() => {
  const unsub = useStore.subscribe(
    (state) => state.notifications,
    (notifications) => {
      notifications.forEach(n => toast(n.message))
    }
  )
  return unsub
}, [])
```

## Transient Updates (No Re-render)

For high-frequency updates (animations, drag), update DOM directly.

```typescript
const countRef = useRef(useStore.getState().count)

useEffect(() => {
  return useStore.subscribe((state) => {
    countRef.current = state.count
    // Update DOM directly
    document.getElementById('count')!.textContent = String(state.count)
  })
}, [])
```

## Context for Store Injection

Use context when you need different store instances (testing, multi-tenant).

```typescript
import { createContext, useContext, useRef } from 'react'
import { createStore, useStore } from 'zustand'

// Create store factory
const createBearStore = (initialBears = 0) => createStore<BearState>((set) => ({
  bears: initialBears,
  increase: () => set((s) => ({ bears: s.bears + 1 })),
}))

type BearStore = ReturnType<typeof createBearStore>

const BearContext = createContext<BearStore | null>(null)

// Provider
function BearProvider({ children, initialBears = 0 }) {
  const storeRef = useRef<BearStore>()
  if (!storeRef.current) {
    storeRef.current = createBearStore(initialBears)
  }
  return (
    <BearContext.Provider value={storeRef.current}>
      {children}
    </BearContext.Provider>
  )
}

// Hook
function useBearStore<T>(selector: (state: BearState) => T): T {
  const store = useContext(BearContext)
  if (!store) throw new Error('Missing BearProvider')
  return useStore(store, selector)
}
```

## Server Components / RSC

Zustand stores are client-side only. For Server Components:

```typescript
// app/page.tsx (Server Component)
async function Page() {
  const data = await fetchData()
  return <ClientComponent initialData={data} />
}

// ClientComponent.tsx
'use client'
import { useEffect } from 'react'

function ClientComponent({ initialData }) {
  const setData = useStore((s) => s.setData)

  // Hydrate store with server data
  useEffect(() => {
    setData(initialData)
  }, [initialData, setData])

  // ...
}
```

### Alternative: Initialize in Provider

```typescript
'use client'
function StoreInitializer({ data }) {
  const initialized = useRef(false)
  if (!initialized.current) {
    useStore.setState({ data })
    initialized.current = true
  }
  return null
}
```

## Performance Tips

1. **Split selectors** - One selector per value when possible
2. **Memoize expensive selectors** - Use useMemo for derived computations
3. **Avoid object/array creation in selectors** - Use useShallow or split
4. **Actions are stable** - No need to memoize or add to deps
5. **Use transient updates** - For animations/drag, bypass React

```typescript
// Actions are stable - this is fine
const increment = useStore((s) => s.increment)
useEffect(() => {
  increment()  // No need for increment in deps
}, [])

// Expensive derived state - memoize
const items = useStore((s) => s.items)
const expensiveResult = useMemo(() =>
  items.filter(complexFilter).map(complexTransform),
  [items]
)
```

## Common Mistakes

```typescript
// MISTAKE 1: Selecting entire state
const state = useStore()  // Re-renders on everything

// MISTAKE 2: Creating objects in selector without useShallow
const { a, b } = useStore(s => ({ a: s.a, b: s.b }))  // Infinite re-renders

// MISTAKE 3: Calling actions directly in render
return <div>{useStore.getState().count}</div>  // Won't update

// MISTAKE 4: Modifying state directly
set((state) => { state.count++ })  // Without immer, this mutates!
```
