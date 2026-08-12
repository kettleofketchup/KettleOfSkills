# Mermaid.js API Reference & Advanced Patterns

JavaScript API methods, event handling, and advanced rendering patterns.

## API Reference

**mermaid.initialize(config)**
Configure global settings.
```javascript
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  logLevel: 3,
  securityLevel: 'strict',
  fontFamily: 'Arial'
});
```

**mermaid.render(id, graphDefinition, config)**
Programmatically render diagram.
```javascript
const { svg, bindFunctions } = await mermaid.render(
  'uniqueId',
  'graph TD\nA-->B',
  { theme: 'forest' }
);
```

**mermaid.parse(text)**
Validate syntax without rendering.
```javascript
try {
  await mermaid.parse('graph TD\nA-->B');
  console.log('Valid');
} catch(e) {
  console.error('Invalid:', e);
}
```

**mermaid.run(config)**
Render all diagrams in page.
```javascript
await mermaid.run({
  querySelector: '.mermaid',
  suppressErrors: false
});
```

## Event Handling

**Click Events:**
```javascript
const graphDefinition = `
  flowchart TD
    A[Click me] --> B
    click A callback "Tooltip text"
`;

window.callback = function() {
  alert('Node clicked!');
};

await mermaid.render('graph', graphDefinition);
```

**Interactive URLs:**
```
flowchart TD
  A[GitHub] --> B[Docs]
  click A "https://github.com"
  click B "https://mermaid.js.org" "Open docs"
```

## Advanced Patterns

**Dynamic Theme Switching:**
```javascript
function updateTheme(isDark) {
  mermaid.initialize({
    theme: isDark ? 'dark' : 'default',
    startOnLoad: false
  });

  // Re-render all diagrams
  document.querySelectorAll('.mermaid').forEach(async (el) => {
    const code = el.textContent;
    const { svg } = await mermaid.render('id', code);
    el.innerHTML = svg;
  });
}
```

**Lazy Loading:**
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(async (entry) => {
    if (entry.isIntersecting) {
      const code = entry.target.textContent;
      const { svg } = await mermaid.render('id', code);
      entry.target.innerHTML = svg;
      observer.unobserve(entry.target);
    }
  });
});

document.querySelectorAll('.mermaid').forEach(el => observer.observe(el));
```

**Server-Side Rendering (SSR):**
```javascript
import { chromium } from 'playwright';

async function renderServerSide(code) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.setContent(`
    <script src="mermaid.min.js"></script>
    <div class="mermaid">${code}</div>
    <script>mermaid.initialize({ startOnLoad: true });</script>
  `);

  const svg = await page.locator('.mermaid svg').innerHTML();
  await browser.close();
  return svg;
}
```
