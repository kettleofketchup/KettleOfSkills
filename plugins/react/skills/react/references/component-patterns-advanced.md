# React Component Patterns: Advanced

## Error Boundaries

Class components only (no hook equivalent yet):

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('Error:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <p>Something went wrong</p>;
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### react-error-boundary Library
```jsx
import { ErrorBoundary, useErrorBoundary } from 'react-error-boundary';

function Fallback({ error, resetErrorBoundary }) {
  return (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={resetErrorBoundary}>Retry</button>
    </div>
  );
}

<ErrorBoundary FallbackComponent={Fallback} onReset={() => refetch()}>
  <DataComponent />
</ErrorBoundary>

// Programmatic error throwing
function ChildComponent() {
  const { showBoundary } = useErrorBoundary();

  async function handleClick() {
    try {
      await riskyOperation();
    } catch (error) {
      showBoundary(error);
    }
  }
}
```

## Portals

Render children outside parent DOM hierarchy:

```jsx
import { createPortal } from 'react-dom';

function Modal({ children, isOpen }) {
  if (!isOpen) return null;

  return createPortal(
    <div className="modal-overlay">
      <div className="modal-content">
        {children}
      </div>
    </div>,
    document.body
  );
}

// Events still bubble through React tree (not DOM tree)
<div onClick={() => console.log('clicked')}>
  <Modal isOpen={true}>
    <button>Click me</button> {/* onClick bubbles to parent div */}
  </Modal>
</div>
```

### Tooltip Example
```jsx
function Tooltip({ children, content, targetRef }) {
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useLayoutEffect(() => {
    if (targetRef.current) {
      const rect = targetRef.current.getBoundingClientRect();
      setPosition({ top: rect.bottom + 8, left: rect.left });
    }
  }, [targetRef]);

  return createPortal(
    <div className="tooltip" style={position}>
      {content}
    </div>,
    document.body
  );
}
```

## Higher-Order Components

Still useful for cross-cutting concerns (prefer hooks when possible):

```jsx
function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const { user, isLoading } = useAuth();

    if (isLoading) return <Loading />;
    if (!user) return <Navigate to="/login" />;

    return <Component {...props} user={user} />;
  };
}

const ProtectedDashboard = withAuth(Dashboard);
```

### When to Use HOCs vs Hooks

**Prefer Hooks:**
- Sharing stateful logic
- Most cases

**Prefer HOCs:**
- Wrapping with providers/contexts
- Adding props conditionally
- Route-level concerns (auth guards)

## Context Pattern

```jsx
const ThemeContext = createContext(null);

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const value = useMemo(() => ({ theme, setTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be within ThemeProvider');
  return context;
}

// Usage
<ThemeProvider>
  <App />
</ThemeProvider>

function Button() {
  const { theme, setTheme } = useTheme();
  return <button className={theme}>Toggle</button>;
}
```
