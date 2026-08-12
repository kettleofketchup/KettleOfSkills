# Zustand Async Actions

## Basic Async Action

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

## Async with Abort/Cancel

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

## Optimistic Updates

```typescript
const useStore = create<Store>((set, get) => ({
  todos: [],

  addTodo: async (text) => {
    const optimisticTodo = { id: `temp-${Date.now()}`, text, done: false }
    const prevTodos = get().todos

    set({ todos: [...prevTodos, optimisticTodo] })

    try {
      const res = await fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify({ text }),
      })
      const realTodo = await res.json()
      set((state) => ({
        todos: state.todos.map(t =>
          t.id === optimisticTodo.id ? realTodo : t
        ),
      }))
    } catch (err) {
      set({ todos: prevTodos })  // Rollback on error
    }
  },
}))
```

## Request Deduplication

```typescript
const useStore = create<Store>((set, get) => ({
  data: null,
  loading: false,
  promise: null,

  fetchData: async () => {
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

## Integration with React Query / SWR

Zustand for client state, React Query/SWR for server state.

```typescript
const useUIStore = create<UIStore>((set) => ({
  selectedId: null,
  setSelectedId: (id) => set({ selectedId: id }),
}))

function useUsers() {
  return useQuery(['users'], fetchUsers)
}

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
