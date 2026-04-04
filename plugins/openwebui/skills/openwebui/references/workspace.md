# Workspace Features Reference

## Models

### Creating / Editing Models
Entry: **+ New Model** button or ellipsis menu on existing card

#### Core Configuration

| Setting | Purpose |
|---------|---------|
| Avatar Photo | Custom image (GIF/WebP animated supported) |
| Model Name & ID | Display name + unique identifier |
| Base Model | Underlying model powering the agent |
| Description | Short summary of model function |
| Tags | Organization in selector dropdown |
| Visibility & Groups | Private access or group-specific controls |

**Fallback**: If base model unavailable and `ENABLE_CUSTOM_MODEL_FALLBACK=True`, system switches to first default model.

#### System Prompt Dynamic Variables (Jinja2-style)

| Variable | Output Example |
|----------|---------------|
| `{{ CURRENT_DATE }}` | `2024-10-27` |
| `{{ CURRENT_TIME }}` | `14:30:05` |
| `{{ USER_NAME }}` | `Admin` |

#### Capabilities

| Capability | Function |
|------------|----------|
| Vision | Image analysis (requires vision-capable base model) |
| Web Search | Access configured search provider |
| File Upload | Allow user file uploads |
| File Context | Process files via RAG (default on) |
| Code Interpreter | Enable Python code execution |
| Image Generation | Enable image generation integration |
| Usage/Citations | Toggle tracking and source citations |
| Status Updates | Show progress steps |
| Builtin Tools | Auto-inject system tools in native function calling mode |

#### Knowledge, Tools, Skills Binding
- Attach Knowledge Collections or Files; toggle "Focused Retrieval" vs "Using Entire Document"
- Force specific tools enabled by default
- Bind Skills with automatic manifest injection
- Attach Pipelines (Profanity Filter, PII Redaction)

### Global Model Management (Admin)

#### View Filters
All | Enabled | Disabled | Visible | Hidden

#### Global Defaults

`DEFAULT_MODEL_METADATA` -- baseline capabilities (vision, web search, file context, code interpreter, builtin tools)

`DEFAULT_MODEL_PARAMS` -- baseline inference params (temperature, top_p, max_tokens, seed, function_calling)

**Merge behavior**:

| Type | Strategy |
|------|----------|
| Capabilities | Deep merge (both global + model applied) |
| Other metadata | Fill-only (global applied when model value is `None`) |
| Parameters | Simple merge (model overrides global) |

---

## Prompts

### Prompt Configuration Fields

| Field | Purpose |
|-------|---------|
| Name | Descriptive identifier |
| Tags | Categorization for filtering |
| Access | Visibility and usage permissions |
| Command | Slash command trigger (e.g., `/summarize`) |
| Prompt Content | Text sent to the model |
| Commit Message | Optional change description for versioning |

### System Variables (Auto-Replaced)

| Category | Variables |
|----------|-----------|
| Clipboard | `{{CLIPBOARD}}` |
| Date/Time | `{{CURRENT_DATE}}`, `{{CURRENT_DATETIME}}`, `{{CURRENT_TIME}}`, `{{CURRENT_TIMEZONE}}`, `{{CURRENT_WEEKDAY}}` |
| User Info | `{{USER_NAME}}`, `{{USER_EMAIL}}`, `{{USER_BIO}}`, `{{USER_GENDER}}`, `{{USER_BIRTH_DATE}}`, `{{USER_AGE}}`, `{{USER_LANGUAGE}}`, `{{USER_LOCATION}}` |

### Custom Input Variable Types

| Type | Properties | Example |
|------|------------|---------|
| `text` | `placeholder`, `default`, `required` | `{{name \| text:placeholder="Enter name":required}}` |
| `textarea` | `placeholder`, `default`, `required` | `{{desc \| textarea:required}}` |
| `select` | `options` (JSON array), `placeholder`, `default`, `required` | `{{priority \| select:options=["High","Medium","Low"]}}` |
| `number` | `placeholder`, `min`, `max`, `step`, `default`, `required` | `{{count \| number:min=1:max=100}}` |
| `checkbox` | `label`, `default` (boolean), `required` | `{{flag \| checkbox:label="Include details"}}` |
| `date` | `placeholder`, `default` (YYYY-MM-DD), `required` | `{{start \| date:required}}` |
| `datetime-local` | `placeholder`, `default`, `required` | `{{appt \| datetime-local}}` |
| `color` | `default` (hex), `required` | `{{brand \| color:default="#FFFFFF"}}` |
| `email` | `placeholder`, `default`, `required` | `{{email \| email:required}}` |
| `range` | `min`, `max`, `step`, `default`, `required` | `{{score \| range:min=1:max=10}}` |
| `url` | `placeholder`, `default`, `required` | `{{site \| url:required}}` |
| `map` | `default` (e.g., "51.5,-0.09"), `required` | `{{location \| map}}` (experimental) |

### Prompt Modifiers (Character-Based Truncation)

| Modifier | Function |
|----------|----------|
| `{{prompt:start:N}}` | First N characters |
| `{{prompt:end:N}}` | Last N characters |
| `{{prompt:middletruncate:N}}` | First + last half (N total chars) |

### Messages Variable Modifiers

**Message Selectors** (`:`) -- control message count:

| Selector | Example |
|----------|---------|
| `START:N` | `{{MESSAGES:START:5}}` -- first 5 messages |
| `END:N` | `{{MESSAGES:END:5}}` -- last 5 messages |
| `MIDDLETRUNCATE:N` | `{{MESSAGES:MIDDLETRUNCATE:6}}` -- 3 first + 3 last |

**Pipe Filters** (`|`) -- control characters per message:

| Filter | Example |
|--------|---------|
| `\|start:N` | `{{MESSAGES\|start:300}}` -- first 300 chars/msg |
| `\|end:N` | `{{MESSAGES\|end:300}}` -- last 300 chars/msg |
| `\|middletruncate:N` | `{{MESSAGES\|middletruncate:500}}` -- 500 chars/msg |

**Combined**: `{{MESSAGES:END:2|middletruncate:500}}` -- last 2 messages, 500 chars each

### Versioning
Every save creates a new version. History sidebar: commit message, author, timestamp, Live badge. Can preview, set as production, delete (except active), copy ID.

---

## Knowledge

### Retrieval Modes

| Mode | Behavior |
|------|----------|
| **Focused Retrieval** (default) | RAG identifies relevant chunks; hybrid search (BM25 + vector) with reranking |
| **Full Context** | Injects complete file; bypasses RAG/chunking; always injected regardless of native FC |

### Native Mode (Agentic) Tools

| Tool | With Attached KB | Without KB |
|------|-----------------|------------|
| `list_knowledge` | Yes | No |
| `list_knowledge_bases` | No | Yes |
| `search_knowledge_bases` | No | Yes |
| `query_knowledge_bases` | No | Yes |
| `search_knowledge_files` | Yes (scoped) | Yes |
| `query_knowledge_files` | Yes (scoped) | Yes |
| `view_file` / `view_knowledge_file` | Yes | No |

**Critical**: With Native Function Calling, attached knowledge is **NOT automatically injected**. Model must actively call knowledge tools. Solutions:
1. Add system prompt instructions directing tool usage
2. Disable native function calling (restores auto RAG injection)
3. Select "Full Context" mode to bypass RAG

### API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/files/` | Upload files |
| `GET /api/v1/files/{id}/process/status` | Check processing status |
| `POST /api/v1/knowledge/{id}/file/add` | Add file to knowledge base |

---

## Skills

Reusable **markdown-based instruction sets** attachable to models or invoked on-the-fly. Unlike Tools (executable Python), Skills are plain-text instructions.

**User-Selected (`$` Mention)**: Full content injected directly into system prompt.

**Model-Attached**: Lazy-loading -- only name + description (manifest) enters system prompt. Model receives `view_skill` builtin tool to load full instructions on demand.

| Field | Description |
|-------|-------------|
| Name | Human-readable display name |
| Skill ID | Unique slug (auto-generated, editable at creation only) |
| Description | Short summary for manifest |
| Content | Full instructions in Markdown |

Import `.md` files with optional YAML frontmatter (`name`, `description`). Active/inactive toggle. Private by default with `read`/`write` sharing.

---

## Notes

Persistent workspace for content outside individual conversations.

| Feature | Description |
|---------|-------------|
| Rich editor | Markdown and Rich Text with floating toolbar |
| AI Enhance | In-place text improvement on selected text |
| Chat sidebar | Dedicated AI conversation about note content |
| Context injection | Attach notes to any chat (full content, no chunking) |
| Export | `.txt`, `.md`, `.pdf` |

### Agentic Note Tools (Native Function Calling)

| Tool | Function |
|------|----------|
| `search_notes` | Search by title/content |
| `view_note` | Read full note content |
| `write_note` | Create new note |
| `replace_note_content` | Update existing note |

Quick creation: `/notes/new?title=My%20Title&content=Initial%20text`

---

## Channels

Persistent shared spaces where humans and AI models participate in real-time conversation.

| Feature | Purpose |
|---------|---------|
| `@model` tagging | Summon AI on demand |
| Threads & reactions | Organized discussions with pins and emoji |
| File sharing | Images, docs, code visible to AI |
| Access control | Public, private, group-based, DM |

Types: Standard (topic rooms), Group (team-scoped), Direct Message (1:1 or small-group)

Setup: Admin Panel > Settings > General > Toggle **Channels (Beta)** on

---

## Open Terminal

Connects computing environment to Open WebUI for AI code execution, file management, and system automation.

### Setup
1. Start Open Terminal instance (Docker or pip)
2. Connect as **User Tool Server** (Settings > Tools) or **Global Tool Server** (Admin Settings > Integrations)

Requires models with **native function calling** support. Frontier models recommended.

Enterprise: Dedicated instance per user with automatic lifecycle management and resource controls.
