# Zustand Testing Patterns

## Reset Store Between Tests

```typescript
// store.ts
const initialState = { count: 0 }

const useStore = create<Store>((set) => ({
  ...initialState,
  increment: () => set((s) => ({ count: s.count + 1 })),
  reset: () => set(initialState),
}))

export const resetStore = () => useStore.setState(initialState)

// test.ts
import { resetStore } from './store'
beforeEach(() => { resetStore() })
```

## Testing Actions Directly

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

## Testing with React Testing Library

```typescript
import { render, screen } from '@testing-library/react'
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
  beforeEach(() => { useStore.setState({ count: 0 }) })

  it('displays and updates count', async () => {
    render(<Counter />)
    expect(screen.getByTestId('count')).toHaveTextContent('0')
    await userEvent.click(screen.getByRole('button'))
    expect(screen.getByTestId('count')).toHaveTextContent('1')
  })
})
```

## Mocking Store for Component Tests

```typescript
import { create } from 'zustand'

const createMockStore = (overrides = {}) => create<Store>(() => ({
  count: 0,
  increment: vi.fn(),
  ...overrides,
}))

vi.mock('./store', () => ({
  useStore: createMockStore({ count: 5 }),
}))
```

## Testing Async Actions with Mocked Fetch

```typescript
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

## Testing Subscriptions

```typescript
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
