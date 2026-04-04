---
name: react
description: React 19 development with async components, Server Components, and modern patterns. Use when building React components, using hooks (useState, useEffect, use, useOptimistic, useActionState, useTransition), implementing async data fetching, Server/Client Component architecture, form handling with Actions, performance optimization with React Compiler, memoization, code splitting, error boundaries, portals, or working with Next.js App Router integration.
---

# React 19

## Async Components (Server Components)

Server Components are async by default - use `async/await` directly:

```jsx
// Server Component (default - no directive needed)
async function UserProfile({ id }) {
  const user = await db.users.get(id);
  return <div>{user.name}</div>;
}
```

## Client Components

Add `'use client'` for interactivity (hooks, event handlers, browser APIs):

```jsx
'use client';
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

## Server → Client Data Flow

```jsx
// Server Component
async function Page() {
  const dataPromise = fetchData(); // Start fetch, don't await
  return (
    <Suspense fallback={<Loading />}>
      <ClientComponent dataPromise={dataPromise} />
    </Suspense>
  );
}

// Client Component
'use client';
import { use } from 'react';

function ClientComponent({ dataPromise }) {
  const data = use(dataPromise); // Resolves the promise
  return <div>{data.title}</div>;
}
```

## use() Hook

Read promises or context conditionally (unlike other hooks):

```jsx
'use client';
import { use } from 'react';

function Message({ messagePromise }) {
  const message = use(messagePromise);
  return <p>{message}</p>;
}

// Context in conditionals
function Button({ showTheme }) {
  if (showTheme) {
    const theme = use(ThemeContext); // Works in conditionals!
    return <button className={theme}>Click</button>;
  }
  return <button>Click</button>;
}
```

## Form Actions

```jsx
'use client';
import { useActionState } from 'react';

async function submitForm(prevState, formData) {
  const result = await saveToServer(formData);
  return { success: true, message: result };
}

function Form() {
  const [state, formAction, isPending] = useActionState(submitForm, null);
  return (
    <form action={formAction}>
      <input name="email" />
      <button disabled={isPending}>{isPending ? 'Saving...' : 'Submit'}</button>
      {state?.message && <p>{state.message}</p>}
    </form>
  );
}
```

## Optimistic Updates

```jsx
'use client';
import { useOptimistic } from 'react';

function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, { ...newTodo, pending: true }]
  );

  async function action(formData) {
    const todo = { text: formData.get('text') };
    addOptimisticTodo(todo);
    await addTodo(todo);
  }

  return (
    <form action={action}>
      <input name="text" />
      <button>Add</button>
      {optimisticTodos.map(t => (
        <li style={{ opacity: t.pending ? 0.5 : 1 }}>{t.text}</li>
      ))}
    </form>
  );
}
```

## Non-Blocking Updates

```jsx
'use client';
import { useTransition } from 'react';

function TabContainer() {
  const [isPending, startTransition] = useTransition();
  const [tab, setTab] = useState('home');

  function selectTab(nextTab) {
    startTransition(() => setTab(nextTab));
  }

  return (
    <div style={{ opacity: isPending ? 0.7 : 1 }}>
      <TabButton onClick={() => selectTab('home')}>Home</TabButton>
      <TabContent tab={tab} />
    </div>
  );
}
```

## Quick Decision Guide

| Need | Use |
|------|-----|
| Async data fetching | Server Component with `async/await` |
| Interactivity/state | Client Component with `'use client'` |
| Resolve promise in client | `use(promise)` with Suspense |
| Form submission | `useActionState` |
| Optimistic UI | `useOptimistic` |
| Non-blocking updates | `useTransition` |
| Expensive computation | `useMemo` (or React Compiler) |

## References

- `references/async-patterns.md` - Server Components, use(), Suspense, Actions, streaming
- `references/hooks.md` - All React 19 hooks with examples
- `references/performance.md` - React Compiler, memoization, code splitting
- `references/component-patterns-composition.md` - Children, compound components, slots, render props, forwarding refs
- `references/component-patterns-advanced.md` - Error boundaries, portals, HOCs, context pattern
