# Rich UI Element Embedding

Tools and Actions support rich UI element embedding -- returning HTML content and interactive iframes that display directly within chat conversations. When a function returns an `HTMLResponse` with `Content-Disposition: inline` header, the content is embedded as an interactive iframe.

## Tool Usage

```python
from fastapi.responses import HTMLResponse

def create_visualization_tool(self, data: str) -> HTMLResponse:
    """
    Creates an interactive data visualization.
    :param data: The data to visualize
    """
    html_content = """
    <!DOCTYPE html>
    <html><head><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>
    <body><div id="chart" style="width:100%;height:400px;"></div>
    <script>Plotly.newPlot('chart', [{y: [1,2,3,4], type: 'scatter'}]);</script></body></html>
    """
    return HTMLResponse(content=html_content, headers={"Content-Disposition": "inline"})
```

### Custom Result Context

Return a tuple of `(HTMLResponse, context)` to provide the LLM with actionable context:

```python
def create_chart(self, data: str) -> tuple:
    html_content = "<html>...</html>"
    result_context = {"status": "success", "chart_type": "scatter", "data_points": 42}
    return HTMLResponse(content=html_content, headers={"Content-Disposition": "inline"}), result_context
```

Context can be: string (as-is), dict (JSON), or list (JSON).

## Action Usage

```python
async def action(self, body, __event_emitter__=None):
    html = "<html><body><h1>Dashboard</h1></body></html>"
    return HTMLResponse(content=html, headers={"Content-Disposition": "inline"})
```

Or tuple with headers:
```python
async def action(self, body, __event_emitter__=None):
    html = "<h1>Interactive Chart</h1><script>...</script>"
    return (html, {"Content-Disposition": "inline", "Content-Type": "text/html"})
```

## Iframe Height - postMessage (Recommended)

```html
<script>
  function reportHeight() {
    const h = document.documentElement.scrollHeight;
    parent.postMessage({ type: 'iframe:height', height: h }, '*');
  }
  window.addEventListener('load', reportHeight);
  new ResizeObserver(reportHeight).observe(document.body);
</script>
```

Add this to every Rich UI embed. Without it, iframe stays at small default height.

## Sandbox and Security

Default sandbox flags: `allow-scripts`, `allow-popups`, `allow-downloads`.

User-toggleable settings (off by default):
- **Allow Iframe Same-Origin Access**: lets iframe access parent page context
- **Allow Iframe Form Submissions**: allows form submissions

When `allowSameOrigin` is off (default): iframe is fully isolated, must use postMessage for height.
When on: auto-resizing works, Chart.js/Alpine.js auto-injected, but iframe can access parent page.

## Rendering Position

- **Tool embeds**: inline at the tool call indicator
- **Action embeds**: above the message text content

## Advanced Communication

### Payload Requests

```html
<script>
  window.addEventListener('message', (e) => {
    if (e.data?.type === 'payload') { const data = e.data.payload; }
  });
  parent.postMessage({ type: 'payload', requestId: 'my-request' }, '*');
</script>
```

### Tool Args Injection (Tools Only)

Tool call arguments are automatically injected into `window.args` in the iframe.

### Auto-Injected Libraries (Same-Origin Only)

When `allowSameOrigin` is enabled:
- **Alpine.js** -- Detected when any `x-data`, `x-init`, `x-show`, etc. directives found
- **Chart.js** -- Detected when `new Chart(` or `Chart.` appears

### Prompt Submission

| Message Type | Behavior |
|---|---|
| `input:prompt` | Fills chat input (no submit) |
| `input:prompt:submit` | Fills and submits prompt |
| `action:submit` | Submits current text in chat input |

Same-origin: `input:prompt:submit` submits immediately.
Cross-origin: shows confirmation dialog first.

## CORS and Direct Tools

For browser-based direct tools, set `Access-Control-Expose-Headers: Content-Disposition` on the tool server.

## Rich UI Embeds vs Execute Event

| | Rich UI Embed | `execute` Event |
|---|---|---|
| **Runs in** | Sandboxed iframe | Main page context |
| **Persistence** | Saved in chat history | Gone on reload |
| **Page access** | Isolated by default | Full access |
| **Best for** | Persistent charts, dashboards | Transient interactions, downloads |
