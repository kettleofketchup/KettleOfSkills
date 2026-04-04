# Async Patterns in React 19

## Server Components

Default component type - render on server, never sent to browser.

```jsx
// No directive needed - Server Component by default
async function ProductPage({ id }) {
  const product = await db.products.get(id);
  const reviews = await db.reviews.getByProduct(id);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <ReviewList reviews={reviews} />
    </div>
  );
}
```

**Benefits:**
- Direct database/filesystem access
- Heavy libraries stay server-side (zero client bundle impact)
- Secrets/tokens never exposed
- No waterfall requests

**Limitations:**
- No `useState`, `useEffect`, or event handlers
- No browser APIs
- Props passed to Client Components must be serializable

## The use() Hook

Read promises and context anywhere (including conditionals/loops):

```jsx
'use client';
import { use } from 'react';

// Reading promises
function Comments({ commentsPromise }) {
  const comments = use(commentsPromise);
  return comments.map(c => <Comment key={c.id} {...c} />);
}

// Context in conditionals (impossible with useContext)
function ThemeButton({ showTheme }) {
  if (showTheme) {
    const theme = use(ThemeContext);
    return <button className={theme}>Styled</button>;
  }
  return <button>Plain</button>;
}
```

**Rules:**
- Must be inside component/hook (not regular functions)
- Cannot be in try-catch (use Error Boundary instead)
- Create promises in Server Components, pass to Client

## Suspense

Declarative loading states:

```jsx
import { Suspense } from 'react';

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <AsyncComponent />
    </Suspense>
  );
}

// Nested Suspense for granular loading
function Dashboard() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>
      <Suspense fallback={<MainSkeleton />}>
        <MainContent />
      </Suspense>
    </div>
  );
}
```

**Streaming Pattern:**
```jsx
// Server Component
async function Page() {
  const criticalData = await getCritical(); // Blocks
  const deferredPromise = getNonCritical(); // Starts, doesn't block

  return (
    <div>
      <Critical data={criticalData} />
      <Suspense fallback={<Loading />}>
        <Deferred dataPromise={deferredPromise} />
      </Suspense>
    </div>
  );
}
```

## Form Actions with useActionState

```jsx
'use client';
import { useActionState } from 'react';

async function createUser(prevState, formData) {
  const email = formData.get('email');

  try {
    await api.createUser({ email });
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

function SignupForm() {
  const [state, formAction, isPending] = useActionState(createUser, null);

  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      <button disabled={isPending}>
        {isPending ? 'Creating...' : 'Sign Up'}
      </button>
      {state?.error && <p className="error">{state.error}</p>}
      {state?.success && <p className="success">Account created!</p>}
    </form>
  );
}
```

**Action receives:** `(previousState, formData) => newState`

## useFormStatus

Access parent form state from nested components:

```jsx
'use client';
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending, data, method, action } = useFormStatus();
  return (
    <button disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

function Form() {
  return (
    <form action={submitAction}>
      <input name="name" />
      <SubmitButton /> {/* Automatically knows form state */}
    </form>
  );
}
```

## Server Actions

Functions that run on server, callable from client:

```jsx
// actions.js
'use server';

export async function addToCart(productId) {
  const cart = await db.cart.add(productId);
  revalidatePath('/cart');
  return cart;
}

// Client Component
'use client';
import { addToCart } from './actions';

function AddButton({ productId }) {
  return (
    <form action={addToCart.bind(null, productId)}>
      <button>Add to Cart</button>
    </form>
  );
}
```

## Error Handling

```jsx
'use client';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <ErrorBoundary fallback={<p>Something went wrong</p>}>
      <Suspense fallback={<Loading />}>
        <AsyncContent />
      </Suspense>
    </ErrorBoundary>
  );
}

// Or handle with .catch() on promise
const safePromise = fetchData().catch(() => ({ fallback: true }));
```

## Next.js Integration

```jsx
// app/page.jsx - Server Component by default
export default async function Page() {
  const data = await fetch('https://api.example.com/data');
  return <Content data={data} />;
}

// app/components/interactive.jsx
'use client';
export function Interactive() {
  const [state, setState] = useState();
  // Client-side interactivity
}
```

**Route Handlers:**
```jsx
// app/api/data/route.js
export async function GET(request) {
  const data = await db.query();
  return Response.json(data);
}
```
