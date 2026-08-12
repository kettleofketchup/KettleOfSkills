# Mermaid.js Configuration Options

Core configuration, security, layout algorithms, and validation.

## Configuration Methods

**1. Site-wide Initialization:**
```javascript
mermaid.initialize({
  theme: 'dark',
  startOnLoad: true,
  securityLevel: 'strict',
  fontFamily: 'Arial'
});
```

**2. Diagram-level Frontmatter:**
````markdown
```mermaid
---
theme: forest
look: handDrawn
---
flowchart TD
  A --> B
```
````

**3. Configuration Hierarchy:**
Default config → Site config → Diagram config (highest priority)

## Core Options

**Rendering:**
- `startOnLoad`: Auto-render on page load (default: true)
- `securityLevel`: "strict" (default), "loose", "antiscript", "sandbox"
- `deterministicIds`: Reproducible SVG IDs (default: false)
- `maxTextSize`: Max diagram text (default: 50000)
- `maxEdges`: Max drawable edges (default: 500)

**Visual Style:**
- `look`: "classic" (default), "handDrawn"
- `handDrawnSeed`: Numeric seed for hand-drawn consistency
- `darkMode`: Boolean toggle

**Typography:**
- `fontFamily`: "trebuchet ms, verdana, arial, sans-serif" (default)
- `fontSize`: Base text size (default: 16)

**Layout:**
- `layout`: "dagre" (default), "elk", "tidy-tree", "cose-bilkent"

**Debug:**
- `logLevel`: 0-5 from trace to fatal
- `htmlLabels`: Enable HTML in labels (default: false)

## Layout Algorithms

**dagre (default):** Standard hierarchical layout for most diagrams.

**elk:** Advanced layout with better handling of complex graphs.

**tidy-tree:** Clean tree structures for hierarchies.

**cose-bilkent:** Compound graph layout for nested structures.

**Per-diagram Configuration:**
````markdown
```mermaid
---
layout: elk
---
flowchart TD
  A --> B
```
````

## Security

**Security Levels:**
- `strict` - HTML encoding (default, recommended)
- `loose` - Some HTML allowed
- `antiscript` - Filter scripts
- `sandbox` - Sandboxed mode

**DOMPurify:**
Enabled by default for XSS protection. Customize via `dompurifyConfig` (use caution).

## Common Patterns

**Consistent Hand-drawn Style:**
```javascript
mermaid.initialize({
  look: 'handDrawn',
  handDrawnSeed: 42  // Same seed = consistent appearance
});
```

**Dark Mode Toggle:**
```javascript
const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
mermaid.initialize({
  theme: isDark ? 'dark' : 'default'
});
```

**Performance Optimization:**
```javascript
mermaid.initialize({
  startOnLoad: false,  // Manual rendering
  maxEdges: 1000,       // Increase for complex graphs
  deterministicIds: true  // Caching-friendly
});
```

## Validation

**Parse without Rendering:**
```javascript
try {
  await mermaid.parse('graph TD\nA-->B');
  console.log('Valid syntax');
} catch(e) {
  console.error('Invalid:', e);
}
```

**Programmatic Rendering:**
```javascript
const { svg } = await mermaid.render('graphId', 'graph TD\nA-->B');
document.getElementById('output').innerHTML = svg;
```
