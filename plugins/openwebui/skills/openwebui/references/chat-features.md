# Chat Features Reference

## Code Execution

### Backends

| Backend | Location | Isolation | Recommended |
|---------|----------|-----------|-------------|
| Pyodide (default) | Browser/WASM | Browser sandbox | Yes (safe default) |
| Jupyter (legacy) | Server | None (shared) | No |
| Open Terminal | Server/Docker | Container-level | Small teams |
| Terminals | Server/orchestrated | Container-per-user | Enterprise |

Code Interpreter and Open Terminal toggles are mutually exclusive.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CODE_INTERPRETER` | `true` | Global enable/disable |
| `CODE_INTERPRETER_ENGINE` | `pyodide` | `pyodide` or `jupyter` |
| `CODE_INTERPRETER_PROMPT_TEMPLATE` | (built-in) | Custom prompt template |
| `CODE_INTERPRETER_BLACKLISTED_MODULES` | `""` | Comma-separated blocked modules |

### Pyodide Libraries
micropip, requests, beautifulsoup4, numpy, pandas, matplotlib, seaborn, scikit-learn, scipy, regex, sympy, tiktoken, pytz, plus full stdlib

Virtual filesystem at `/mnt/uploads/` backed by IndexedDB (persists across executions and reloads).

### Inline Image Display
Print `data:image/png;base64,...` to stdout. Open WebUI auto-detects, uploads, replaces with file URL.

---

## Artifacts
Interactive standalone content (HTML, SVG, ThreeJS, D3.js) displayed separately from chat. Version control via selector. If preview fails with SecurityError: Settings > Interface > Toggle "Allow Iframe Sandbox Same-Origin Access".

---

## Multi-Model Chats

| Setting | Value |
|---------|-------|
| `USER_PERMISSIONS_CHAT_MULTIPLE_MODELS` | `True` (default) |

Click `+` in model selector to add models. Responses generate in parallel columns. Merge/synthesize via "Mixture of Agents" button.

---

## Folders & Projects

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_FOLDERS` | `True` | Enable folders |
| `USER_PERMISSIONS_FEATURES_FOLDERS` | `True` | User access |

Folder settings: name, background image, system prompt (prepended to all chats), attached knowledge. Tags: filter via `tag:my-tag-name`.

---

## URL Parameters

| Parameter | Example |
|-----------|---------|
| `models` | `/?models=model1,model2` |
| `model` | `/?model=model1` |
| `youtube` | `/?youtube=VIDEO_ID` |
| `load-url` | `/?load-url=https://example.com` |
| `web-search` | `/?web-search=true` |
| `tools` | `/?tools=tool1,tool2` |
| `call` | `/?call=true` |
| `q` | `/?q=Hello%20there` |
| `temporary-chat` | `/?temporary-chat=true` |
| `code-interpreter` | `/?code-interpreter=true` |
| `image-generation` | `/?image-generation=true` |

---

## Chat Parameters Hierarchy

| Level | Location | Override |
|-------|----------|----------|
| Per-Chat | Right sidebar Chat Controls | Cannot override model-specific |
| Per-Account | Settings > General | Can be overridden by per-model |
| Per-Model | Workspace > Models (admin) | Takes precedence over all |

---

## Reasoning & Thinking Models

Default tags: `<think>`, `<thinking>`, `<reason>`, `<reasoning>`, `<thought>`, `<|begin_of_thought|>`

Configurable via `reasoning_tags` parameter per-chat or per-model. Tags stripped before sending to LLM. Content preserved across turns.

Ollama: use `--reasoning-parser deepseek_r1` (or `qwen3`/`deepseek_v3`). Reasoning effort: `low`/`medium`/`high`.

---

## Temporal Awareness

### System Variables (Auto-Injected)
`{{CURRENT_DATE}}` (YYYY-MM-DD), `{{CURRENT_TIME}}` (HH:MM), `{{CURRENT_WEEKDAY}}`

### Native Tools (Agentic)
`get_current_timestamp` -- Unix timestamp + ISO date. `calculate_timestamp` -- relative time arithmetic.

---

## Autocomplete
Sends input to Task Model during typing pauses. Accept: `Tab`/`Right Arrow`. Use small fast models (Llama 3.2 1B/3B, Qwen 3 0.6B). Config: Admin Settings > Interface > Task Model.

---

## Follow-Up Prompts
Auto-generated after model responses via task model. Settings > Interface > Chat: toggle auto-generation, persistence, insert-to-input behavior.

---

## Message Queue
Compose messages while AI generates. Queued messages combined into single prompt on completion. Saved via session storage. Settings > Interface > Chat: toggle queue mode vs interrupt mode.

---

## Chat Sharing
Admin Panel > Settings > General > "Enable Community Sharing". Link sharing creates static snapshot. Recipients need active accounts on the instance.

---

## History & Search
Shortcut: `Cmd+K`/`Ctrl+K`. Fuzzy search across titles, content, tags. Native tools: `search_chats`, `view_chat` (with Native Function Calling).
