# Zustand Async Actions & Testing

## Async Actions

### Basic Async Action

```typescript
interface Store {
  users: User[]
  loading: boolean
  error: string | null
  fetchUsers: () => Promise<void>
}

const useStore = create<Store>((set) => ({
  users: [],
  loading: false,
  error: null,

  fetchUsers: async () => {
    set({ loading: true, error: null })
    try {
      const res = await fetch('/api/users')
      const users = await res.json()
      set({ users, loading: false })
    } catch (err) {
      set({ error: err.message, loading: false })
    }
  },
}))
```

### Async with Abort/Cancel

```typescript
interface Store {
  data: Data | null
  loading: boolean
  abortController: AbortController | null
  fetchData: () => Promise<void>
  cancel: () => void
}

const useStore = create<Store>((set, get) => ({
  data: null,
  loading: false,
  abortController: null,

  fetchData: async () => {
    // Cancel any in-flight request
    get().abortController?.abort()

    const controller = new AbortController()
    set({ loading: true, abortController: controller })

    try {
      const res = await fetch('/api/data', { signal: controller.signal })
      const data = await res.json()
      set({ data, loading: false, abortController: null })
    } catch (err) {
      if (err.name !== 'AbortError') {
        set({ loading: false, abortController: null })
      }
    }
  },

  cancel: () => {
    get().abortController?.abort()
    set({ loading: false, abortController: null })
  },
}))
```

### Optimistic Updates

```typescript
interface Store {
  todos: Todo[]
  addTodo: (text: string) => Promise<void>
}

const useStore = create<Store>((set, get) => ({
  todos: [],

  addTodo: async (text) => {
    const optimisticTodo = { id: `temp-${Date.now()}`, text, done: false }
    const prevTodos = get().todos

    // Optimistic update
    set({ todos: [...prevTodos, optimisticTodo] })

    try {
      const res = await fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify({ text }),
      })
      const realTodo = await res.json()

      // Replace optimistic with real
      set((state) => ({
        todos: state.todos.map(t =>
          t.id === optimisticTodo.id ? realTodo : t
        ),
      }))
    } catch (err) {
      // Rollback on error
      set({ todos: prevTodos })
    }
  },
}))
```

### Request Deduplication

```typescript
interface Store {
  data: Data | null
  loading: boolean
  promise: Promise<Data> | null
  fetchData: () => Promise<Data>
}

const useStore = create<Store>((set, get) => ({
  data: null,
  loading: false,
  promise: null,

  fetchData: async () => {
    // Return existing promise if request in flight
    const existing = get().promise
    if (existing) return existing

    const promise = fetch('/api/data').then(r => r.json())
    set({ loading: true, promise })

    try {
      const data = await promise
      set({ data, loading: false, promise: null })
      return data
    } catch (err) {
      set({ loading: false, promise: null })
      throw err
    }
  },
}))
```

## Testing Zustand Stores

### Reset Store Between Tests

```typescript
// store.ts
const initialState = { count: 0 }

const useStore = create<Store>((set) => ({
  ...initialState,
  increment: () => set((s) => ({ count: s.count + 1 })),
  reset: () => set(initialState),
}))

// Expose for testing
export const resetStore = () => useStore.setState(initialState)

// test.ts
import { resetStore } from './store'

beforeEach(() => {
  resetStore()
})
```

### Testing Actions Directly

```typescript
import { useStore } from './store'

describe('store', () => {
  beforeEach(() => {
    useStore.setState({ count: 0 })
  })

  it('increments count', () => {
    useStore.getState().increment()
    expect(useStore.getState().count).toBe(1)
  })

  it('handles async action', async () => {
    await useStore.getState().fetchData()
    expect(useStore.getState().data).toBeDefined()
  })
})
```

### Testing with React Testing Library

```typescript
import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useStore } from './store'

function Counter() {
  const count = useStore((s) => s.count)
  const increment = useStore((s) => s.increment)
  return (
    <div>
      <span data-testid="count">{count}</span>
      <button onClick={increment}>+</button>
    </div>
  )
}

describe('Counter', () => {
  beforeEach(() => {
    useStore.setState({ count: 0 })
  })

  it('displays and updates count', async () => {
    render(<Counter />)

    expect(screen.getByTestId('count')).toHaveTextContent('0')

    await userEvent.click(screen.getByRole('button'))

    expect(screen.getByTestId('count')).toHaveTextContent('1')
  })
})
```

### Mocking Store for Component Tests

```typescript
import { create } from 'zustand'

// Create mock store for tests
const createMockStore = (overrides = {}) => create<Store>(() => ({
  count: 0,
  increment: vi.fn(),
  ...overrides,
}))

// In test file
vi.mock('./store', () => ({
  useStore: createMockStore({ count: 5 }),
}))
```

### Testing Async Actions with Mocked Fetch

```typescript
import { useStore } from './store'

describe('async actions', () => {
  beforeEach(() => {
    useStore.setState({ users: [], loading: false, error: null })
    global.fetch = vi.fn()
  })

  it('fetches users successfully', async () => {
    const mockUsers = [{ id: '1', name: 'John' }]
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      json: () => Promise.resolve(mockUsers),
    })

    await useStore.getState().fetchUsers()

    expect(useStore.getState().users).toEqual(mockUsers)
    expect(useStore.getState().loading).toBe(false)
  })

  it('handles fetch error', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    await useStore.getState().fetchUsers()

    expect(useStore.getState().error).toBe('Network error')
    expect(useStore.getState().loading).toBe(false)
  })
})
```

### Testing Subscriptions

```typescript
import { useStore } from './store'

describe('subscriptions', () => {
  it('notifies subscribers on state change', () => {
    const listener = vi.fn()
    const unsub = useStore.subscribe(listener)

    useStore.getState().increment()

    expect(listener).toHaveBeenCalled()
    unsub()
  })

  // With subscribeWithSelector middleware
  it('notifies only when selected state changes', () => {
    const listener = vi.fn()
    const unsub = useStore.subscribe(
      (state) => state.count,
      listener
    )

    useStore.setState({ unrelatedField: 'test' })
    expect(listener).not.toHaveBeenCalled()

    useStore.getState().increment()
    expect(listener).toHaveBeenCalled()

    unsub()
  })
})
```

## Integration with React Query / SWR

Zustand for client state, React Query/SWR for server state.

```typescript
// Zustand for UI state
const useUIStore = create<UIStore>((set) => ({
  selectedId: null,
  setSelectedId: (id) => set({ selectedId: id }),
}))

// React Query for server state
function useUsers() {
  return useQuery(['users'], fetchUsers)
}

// Component combines both
function UserList() {
  const { data: users } = useUsers()
  const selectedId = useUIStore((s) => s.selectedId)
  const setSelectedId = useUIStore((s) => s.setSelectedId)

  return (
    <ul>
      {users?.map(user => (
        <li
          key={user.id}
          className={user.id === selectedId ? 'selected' : ''}
          onClick={() => setSelectedId(user.id)}
        >
          {user.name}
        </li>
      ))}
    </ul>
  )
}
```
