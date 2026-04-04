# React 19 Performance

## React Compiler

Automatic memoization - eliminates need for manual `useMemo`, `useCallback`, `memo()`.

**What it does:**
- Analyzes component render behavior
- Automatically memoizes values and callbacks
- Skips re-renders when props haven't changed

**Installation:**
```bash
npm install -D babel-plugin-react-compiler
```

**Babel config:**
```js
// babel.config.js
module.exports = {
  plugins: ['babel-plugin-react-compiler']
};
```

**Next.js:**
```js
// next.config.js
module.exports = {
  experimental: {
    reactCompiler: true
  }
};
```

**When manual memoization still needed:**
- Complex dependency arrays the compiler can't analyze
- External library integration
- Opting out specific components

## Manual Memoization

### memo() - Memoize Components
```jsx
import { memo } from 'react';

const ExpensiveList = memo(function ExpensiveList({ items }) {
  return items.map(item => <Item key={item.id} {...item} />);
});

// With custom comparison
const List = memo(Component, (prevProps, nextProps) => {
  return prevProps.id === nextProps.id;
});
```

### useMemo - Memoize Values
```jsx
// Expensive computation
const sortedItems = useMemo(
  () => items.sort((a, b) => a.score - b.score),
  [items]
);

// Object/array reference stability
const config = useMemo(() => ({ theme, locale }), [theme, locale]);
```

### useCallback - Memoize Functions
```jsx
const handleClick = useCallback((id) => {
  onSelect(id);
}, [onSelect]);

// Passing to memoized children
<MemoizedChild onClick={handleClick} />
```

## Code Splitting

### lazy() + Suspense
```jsx
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Route-Based Splitting
```jsx
// React Router
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

<Routes>
  <Route path="/dashboard" element={
    <Suspense fallback={<PageLoader />}>
      <Dashboard />
    </Suspense>
  } />
</Routes>
```

### Named Exports
```jsx
// utils.js exports { heavyUtil }
const HeavyUtil = lazy(() =>
  import('./utils').then(module => ({ default: module.heavyUtil }))
);
```

## Transitions

### useTransition - Non-Blocking Updates
```jsx
const [isPending, startTransition] = useTransition();

function handleTabChange(tab) {
  startTransition(() => {
    setActiveTab(tab); // Won't block typing/clicking
  });
}

<div style={{ opacity: isPending ? 0.7 : 1 }}>
  <TabContent tab={activeTab} />
</div>
```

### useDeferredValue - Defer Expensive Renders
```jsx
const deferredQuery = useDeferredValue(searchQuery);

// Input stays responsive, list updates when idle
<input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
<ExpensiveList query={deferredQuery} />
```

## Avoiding Re-renders

### Lift State Down
```jsx
// Bad: Parent re-renders on every keystroke
function Parent() {
  const [text, setText] = useState('');
  return (
    <div>
      <input value={text} onChange={e => setText(e.target.value)} />
      <ExpensiveChild /> {/* Re-renders unnecessarily */}
    </div>
  );
}

// Good: Isolate state
function Parent() {
  return (
    <div>
      <SearchInput /> {/* State lives here */}
      <ExpensiveChild /> {/* Never re-renders from typing */}
    </div>
  );
}
```

### Children as Props
```jsx
// Expensive component won't re-render when Parent state changes
function Parent({ children }) {
  const [count, setCount] = useState(0);
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>{count}</button>
      {children} {/* Stable reference, won't re-render */}
    </div>
  );
}

<Parent>
  <ExpensiveChild />
</Parent>
```

## Profiling

### React DevTools Profiler
1. Open React DevTools → Profiler tab
2. Click record, interact with app, stop
3. Review flame graph for slow components

### console.time
```jsx
function ExpensiveComponent({ data }) {
  console.time('render');
  const result = heavyComputation(data);
  console.timeEnd('render');
  return <div>{result}</div>;
}
```

## Next.js Specific

### Partial Prerendering
Static shell + streaming dynamic content:
```jsx
// Static parts render immediately
// Dynamic parts stream in with Suspense
export default function Page() {
  return (
    <div>
      <StaticHeader />
      <Suspense fallback={<Skeleton />}>
        <DynamicContent />
      </Suspense>
    </div>
  );
}
```

### Server Components for Heavy Libs
```jsx
// This 50KB library never hits client bundle
import { marked } from 'marked';

async function MarkdownPage({ slug }) {
  const content = await getMarkdown(slug);
  return <div dangerouslySetInnerHTML={{ __html: marked(content) }} />;
}
```

### Image Optimization
```jsx
import Image from 'next/image';

<Image
  src="/photo.jpg"
  width={800}
  height={600}
  placeholder="blur"
  loading="lazy"
/>
```
