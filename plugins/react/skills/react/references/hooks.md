# React 19 Hooks Reference

## State Hooks

### useState
```jsx
const [state, setState] = useState(initialValue);
const [state, setState] = useState(() => computeInitial()); // Lazy init

// Functional updates (when new state depends on previous)
setState(prev => prev + 1);
```

### useReducer
```jsx
const [state, dispatch] = useReducer(reducer, initialState);
const [state, dispatch] = useReducer(reducer, initialArg, init); // Lazy init

function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    default: return state;
  }
}
```

### useSyncExternalStore
Subscribe to external stores (Redux, browser APIs):
```jsx
const value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?);

// Example: window width
const width = useSyncExternalStore(
  (cb) => { window.addEventListener('resize', cb); return () => window.removeEventListener('resize', cb); },
  () => window.innerWidth,
  () => 1024 // Server fallback
);
```

## React 19 Async Hooks

### use
Read promises/context anywhere (conditionals, loops):
```jsx
const data = use(promise);      // Suspends until resolved
const theme = use(ThemeContext); // Like useContext but flexible

// In conditionals (unique to use)
if (showData) {
  const data = use(dataPromise);
}
```

### useActionState
Form actions with state management:
```jsx
const [state, formAction, isPending] = useActionState(
  async (prevState, formData) => {
    const result = await submit(formData);
    return { success: true, data: result };
  },
  null // initial state
);

<form action={formAction}>
  <button disabled={isPending}>Submit</button>
  {state?.success && <p>Done!</p>}
</form>
```

### useOptimistic
Optimistic UI updates:
```jsx
const [optimisticItems, addOptimistic] = useOptimistic(
  items,
  (state, newItem) => [...state, { ...newItem, pending: true }]
);

async function onAdd(item) {
  addOptimistic(item);
  await saveItem(item);
}
```

### useFormStatus
Access parent form state (must be child of form):
```jsx
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending, data, method } = useFormStatus();
  return <button disabled={pending}>{pending ? '...' : 'Submit'}</button>;
}
```

## Transition Hooks

### useTransition
Non-blocking state updates:
```jsx
const [isPending, startTransition] = useTransition();

function handleClick() {
  startTransition(() => {
    setExpensiveState(newValue); // Won't block UI
  });
}

// Async transitions
startTransition(async () => {
  await saveData();
  startTransition(() => setState(newValue)); // Wrap post-await updates
});
```

### useDeferredValue
Defer expensive re-renders:
```jsx
const deferredQuery = useDeferredValue(query);
const isStale = query !== deferredQuery;

// Shows stale results while computing new ones
<div style={{ opacity: isStale ? 0.7 : 1 }}>
  <ExpensiveList query={deferredQuery} />
</div>
```

## Effect Hooks

### useEffect
Side effects after render:
```jsx
useEffect(() => {
  const sub = subscribe(id);
  return () => sub.unsubscribe(); // Cleanup
}, [id]); // Re-run when id changes

useEffect(() => { /* runs after every render */ });
useEffect(() => { /* runs once on mount */ }, []);
```

### useLayoutEffect
Synchronous effects before browser paint (DOM measurements):
```jsx
useLayoutEffect(() => {
  const { height } = ref.current.getBoundingClientRect();
  setHeight(height);
}, []);
```

### useInsertionEffect
For CSS-in-JS libraries (before DOM mutations):
```jsx
useInsertionEffect(() => {
  document.head.appendChild(styleElement);
  return () => styleElement.remove();
}, []);
```

## Ref Hooks

### useRef
Mutable ref that persists across renders:
```jsx
const ref = useRef(null);        // DOM ref
const countRef = useRef(0);      // Mutable value (no re-render on change)

<input ref={ref} />
ref.current.focus();
```

### useImperativeHandle
Customize ref exposed to parent:
```jsx
const Input = forwardRef((props, ref) => {
  const inputRef = useRef();

  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current.focus(),
    clear: () => inputRef.current.value = ''
  }), []);

  return <input ref={inputRef} />;
});
```

## Performance Hooks

### useMemo
Memoize expensive computations:
```jsx
const sorted = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);
```

### useCallback
Memoize functions (stable reference):
```jsx
const handleClick = useCallback((id) => {
  setSelected(id);
}, []); // Empty deps = never recreated

// Common pattern: passing to memoized children
<MemoizedChild onClick={handleClick} />
```

## Context Hooks

### useContext
Read context value:
```jsx
const theme = useContext(ThemeContext);
```

**Tip:** `use(ThemeContext)` is more flexible (works in conditionals).

### useId
Generate unique IDs (SSR-safe):
```jsx
function Field({ label }) {
  const id = useId();
  return (
    <>
      <label htmlFor={id}>{label}</label>
      <input id={id} />
    </>
  );
}
```

## Debug Hooks

### useDebugValue
Label custom hooks in React DevTools:
```jsx
function useOnlineStatus() {
  const isOnline = useSyncExternalStore(/*...*/);
  useDebugValue(isOnline ? 'Online' : 'Offline');
  return isOnline;
}
```

## Hook Rules

1. Only call at top level (not in loops, conditions, nested functions)
2. Only call from React functions (components or custom hooks)
3. Exception: `use()` can be called in conditionals/loops
