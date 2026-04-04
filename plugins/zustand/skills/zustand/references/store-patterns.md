# Zustand Store Patterns

## TypeScript Store Setup

### Basic Typed Store

```typescript
import { create } from 'zustand'

interface CounterState {
  count: number
  increment: () => void
  decrement: () => void
  reset: () => void
}

const useCounterStore = create<CounterState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}))
```

### Store with `get` for Reading State in Actions

```typescript
interface TodoState {
  todos: Todo[]
  addTodo: (text: string) => void
  toggleTodo: (id: string) => void
  completedCount: () => number  // derived value via get
}

const useTodoStore = create<TodoState>((set, get) => ({
  todos: [],
  addTodo: (text) => set((state) => ({
    todos: [...state.todos, { id: crypto.randomUUID(), text, done: false }]
  })),
  toggleTodo: (id) => set((state) => ({
    todos: state.todos.map(t => t.id === id ? { ...t, done: !t.done } : t)
  })),
  completedCount: () => get().todos.filter(t => t.done).length,
}))
```

## Slice Pattern (Large Stores)

Split large stores into slices, then combine. Each slice is a function that receives `set` and `get`.

### Define Slices

```typescript
// types.ts
interface UserSlice {
  user: User | null
  setUser: (user: User) => void
  logout: () => void
}

interface CartSlice {
  items: CartItem[]
  addItem: (item: CartItem) => void
  clearCart: () => void
}

type StoreState = UserSlice & CartSlice

// userSlice.ts
import { StateCreator } from 'zustand'

const createUserSlice: StateCreator<StoreState, [], [], UserSlice> = (set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
})

// cartSlice.ts
const createCartSlice: StateCreator<StoreState, [], [], CartSlice> = (set) => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
  clearCart: () => set({ items: [] }),
})
```

### Combine Slices

```typescript
// store.ts
import { create } from 'zustand'

const useStore = create<StoreState>()((...args) => ({
  ...createUserSlice(...args),
  ...createCartSlice(...args),
}))

export default useStore
```

### Slice with Cross-Slice Access

```typescript
// Slice that needs to access other slices
const createCartSlice: StateCreator<StoreState, [], [], CartSlice> = (set, get) => ({
  items: [],
  addItem: (item) => {
    const user = get().user  // Access user slice
    if (!user) throw new Error('Must be logged in')
    set((state) => ({ items: [...state.items, item] }))
  },
  clearCart: () => set({ items: [] }),
})
```

## Multiple Independent Stores

For unrelated state, create separate stores instead of slices.

```typescript
// stores/auth.ts
export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  login: (token) => set({ token }),
  logout: () => set({ token: null }),
}))

// stores/ui.ts
export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}))
```

## Resetting Store State

```typescript
interface StoreState {
  count: number
  name: string
  increment: () => void
  reset: () => void
}

const initialState = {
  count: 0,
  name: '',
}

const useStore = create<StoreState>((set) => ({
  ...initialState,
  increment: () => set((s) => ({ count: s.count + 1 })),
  reset: () => set(initialState),
}))
```

## Computed/Derived Values

### Option 1: Getter function (computed on call)

```typescript
const useStore = create<State>((set, get) => ({
  items: [],
  totalPrice: () => get().items.reduce((sum, i) => sum + i.price, 0),
}))

// Usage
const total = useStore((s) => s.totalPrice())
```

### Option 2: Selector outside store (memoized with useMemo)

```typescript
const useStore = create<State>((set) => ({
  items: [],
}))

// In component
const items = useStore((s) => s.items)
const total = useMemo(() => items.reduce((sum, i) => sum + i.price, 0), [items])
```

### Option 3: subscribeWithSelector for reactive derived state

See `middleware.md` for subscribeWithSelector pattern.

## TypeScript Tips

### Extracting State/Actions Types

```typescript
// Extract full store type
type Store = ReturnType<typeof useStore.getState>

// Extract just state (without actions) - manual approach
type State = Pick<Store, 'count' | 'name'>
type Actions = Omit<Store, keyof State>
```

### Generic Store Factory

```typescript
function createEntityStore<T extends { id: string }>() {
  return create<{
    entities: T[]
    add: (entity: T) => void
    remove: (id: string) => void
  }>((set) => ({
    entities: [],
    add: (entity) => set((s) => ({ entities: [...s.entities, entity] })),
    remove: (id) => set((s) => ({ entities: s.entities.filter(e => e.id !== id) })),
  }))
}

const useUserStore = createEntityStore<User>()
const usePostStore = createEntityStore<Post>()
```
