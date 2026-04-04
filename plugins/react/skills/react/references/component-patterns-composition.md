# React Component Patterns: Composition

## Children Pattern
```jsx
function Card({ children }) {
  return <div className="card">{children}</div>;
}

<Card>
  <h2>Title</h2>
  <p>Content</p>
</Card>
```

## Compound Components
```jsx
function Tabs({ children, defaultTab }) {
  const [active, setActive] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
}

Tabs.List = function TabList({ children }) {
  return <div className="tab-list">{children}</div>;
};

Tabs.Tab = function Tab({ value, children }) {
  const { active, setActive } = useContext(TabsContext);
  return (
    <button
      className={active === value ? 'active' : ''}
      onClick={() => setActive(value)}
    >
      {children}
    </button>
  );
};

Tabs.Panel = function TabPanel({ value, children }) {
  const { active } = useContext(TabsContext);
  return active === value ? <div>{children}</div> : null;
};

// Usage
<Tabs defaultTab="one">
  <Tabs.List>
    <Tabs.Tab value="one">Tab 1</Tabs.Tab>
    <Tabs.Tab value="two">Tab 2</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="one">Content 1</Tabs.Panel>
  <Tabs.Panel value="two">Content 2</Tabs.Panel>
</Tabs>
```

## Slots Pattern
```jsx
function Layout({ header, sidebar, children }) {
  return (
    <div className="layout">
      <header>{header}</header>
      <aside>{sidebar}</aside>
      <main>{children}</main>
    </div>
  );
}

<Layout
  header={<NavBar />}
  sidebar={<Menu />}
>
  <Article />
</Layout>
```

## Render Props (Legacy Pattern)

Hooks usually better, but still useful for render customization:

```jsx
function MouseTracker({ render }) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMove = (e) => setPosition({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  return render(position);
}

// Usage
<MouseTracker render={({ x, y }) => (
  <div>Mouse: {x}, {y}</div>
)} />

// Better: Custom hook
function useMousePosition() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  // ... same logic
  return position;
}
```

## Forwarding Refs

```jsx
const Input = forwardRef(function Input(props, ref) {
  return <input ref={ref} {...props} />;
});

// Parent can access input DOM node
function Form() {
  const inputRef = useRef();
  return (
    <>
      <Input ref={inputRef} />
      <button onClick={() => inputRef.current.focus()}>Focus</button>
    </>
  );
}
```

### With useImperativeHandle
```jsx
const VideoPlayer = forwardRef(function VideoPlayer({ src }, ref) {
  const videoRef = useRef();

  useImperativeHandle(ref, () => ({
    play: () => videoRef.current.play(),
    pause: () => videoRef.current.pause(),
    seek: (time) => videoRef.current.currentTime = time
  }), []);

  return <video ref={videoRef} src={src} />;
});

// Parent uses custom API
function App() {
  const playerRef = useRef();
  return (
    <>
      <VideoPlayer ref={playerRef} src="movie.mp4" />
      <button onClick={() => playerRef.current.play()}>Play</button>
      <button onClick={() => playerRef.current.seek(30)}>Skip to 0:30</button>
    </>
  );
}
```
