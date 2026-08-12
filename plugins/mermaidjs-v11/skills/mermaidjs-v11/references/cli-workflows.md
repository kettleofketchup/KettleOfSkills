# Mermaid.js CLI Workflows

Configuration files, Node.js API, and common CI/CD workflow patterns.

## Configuration Files

**Mermaid Config (JSON):**
```json
{
  "theme": "dark",
  "look": "handDrawn",
  "fontFamily": "Arial",
  "flowchart": {
    "curve": "basis"
  }
}
```

**Usage:**
```bash
mmdc -i input.mmd --configFile config.json -o output.svg
```

**Custom CSS:**
```css
.node rect {
  fill: #f9f;
  stroke: #333;
}
.edgeLabel {
  background-color: white;
}
```

**Usage:**
```bash
mmdc -i input.mmd --cssFile styles.css -o output.svg
```

## Node.js API

**Programmatic Usage:**
```javascript
import { run } from '@mermaid-js/mermaid-cli';

await run('input.mmd', 'output.svg', {
  theme: 'dark',
  backgroundColor: 'transparent'
});
```

**With Options:**
```javascript
import { run } from '@mermaid-js/mermaid-cli';

await run('diagram.mmd', 'output.png', {
  theme: 'forest',
  backgroundColor: '#ffffff',
  cssFile: 'custom.css',
  configFile: 'config.json'
});
```

## Common Workflows

**Documentation Generation:**
```bash
# Convert all diagrams in docs/
find docs/ -name "*.mmd" -exec sh -c \
  'mmdc -i "$1" -o "${1%.mmd}.svg"' _ {} \;
```

**Styled Output:**
```bash
# Create dark-themed transparent diagrams
mmdc -i architecture.mmd -o arch.png \
  -t dark \
  -b transparent \
  --cssFile animations.css
```

**CI/CD Pipeline:**
```yaml
# GitHub Actions example
- name: Generate Diagrams
  run: |
    npm install -g @mermaid-js/mermaid-cli
    mmdc -i docs/diagram.mmd -o docs/diagram.svg
```

**Accessibility-Enhanced:**
```bash
# Diagrams with accTitle/accDescr preserved
mmdc -i accessible-diagram.mmd -o output.svg
```
