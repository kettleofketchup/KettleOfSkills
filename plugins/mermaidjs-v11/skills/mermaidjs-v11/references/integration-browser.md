# Mermaid.js Browser & Framework Integration

HTML embedding, React, Vue, and Markdown integration patterns.

## HTML/Browser Integration

**Basic CDN Setup:**
```html
<head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.min.js"></script>
</head>
<body>
  <pre class="mermaid">
    flowchart TD
      A[Client] --> B[Load Balancer]
      B --> C[Server 1]
  </pre>
  <script>mermaid.initialize({ startOnLoad: true });</script>
</body>
```

**ES Module (Modern):**
```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
```

## NPM/Node.js Integration

```bash
npm install mermaid
```

**Import and Initialize:**
```javascript
import mermaid from 'mermaid';
mermaid.initialize({ startOnLoad: true, theme: 'dark', securityLevel: 'strict' });
```

**Manual Rendering:**
```javascript
import mermaid from 'mermaid';
const graphDefinition = `graph TD\n  A[Start] --> B[Process]\n  B --> C[End]`;
const { svg } = await mermaid.render('graphId', graphDefinition);
document.getElementById('container').innerHTML = svg;
```

## React Integration

**Component Wrapper:**
```jsx
import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

function MermaidDiagram({ chart }) {
  const ref = useRef(null);
  useEffect(() => {
    mermaid.initialize({ startOnLoad: false });
    if (ref.current) {
      mermaid.render('diagram', chart).then(({ svg }) => {
        ref.current.innerHTML = svg;
      });
    }
  }, [chart]);
  return <div ref={ref} />;
}
```

**Next.js (App Router):**
```jsx
'use client';
import dynamic from 'next/dynamic';
const Mermaid = dynamic(() => import('./MermaidDiagram'), { ssr: false });
```

## Vue Integration

```vue
<template><div ref="container"></div></template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import mermaid from 'mermaid';

const props = defineProps(['chart']);
const container = ref(null);

onMounted(() => {
  mermaid.initialize({ startOnLoad: false });
  renderDiagram();
});
watch(() => props.chart, renderDiagram);

async function renderDiagram() {
  const { svg } = await mermaid.render('diagram', props.chart);
  container.value.innerHTML = svg;
}
</script>
```

## Markdown Integration

**GitHub/GitLab:** Use fenced mermaid code blocks natively.

**MDX (Next.js/Gatsby):**
```mdx
import Mermaid from './Mermaid';

<Mermaid chart={`
  flowchart LR
    Client --> API
    API --> Database
`} />
```

## Platform-Specific

**Jupyter/Python:**
```python
from IPython.display import Image
diagram = "graph TD\nA-->B"
url = f"https://mermaid.ink/svg/{diagram}"
Image(url=url)
```

**VS Code:** Install "Markdown Preview Mermaid Support" extension.

**Obsidian:** Native support in fenced mermaid code blocks.

**PowerPoint/Word:** Use mermaid.live editor, export SVG/PNG, then insert image.
