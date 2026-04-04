# Tools

Tools extend an LLM's capabilities beyond simple text generation -- web search, data scraping, image generation, AI voices, and more.

## Tooling Taxonomy

| Type | Location in UI | Best For | Source |
| :--- | :--- | :--- | :--- |
| **Native Features** | Admin/Settings | Core platform functionality | Built-in |
| **Workspace Tools** | `Workspace > Tools` | User-created or community Python scripts | Community Library |
| **Native MCP (HTTP)** | `Settings > Connections` | Standard MCP servers via HTTP/SSE | External MCP Servers |
| **MCP via Proxy (MCPO)** | `Settings > Connections` | Local stdio-based MCP servers | MCPO Adapter |
| **OpenAPI Servers** | `Settings > Connections` | Standard REST/OpenAPI web services | External Web APIs |
| **Open Terminal** | `Settings > Integrations` | Full shell access in isolated Docker container | Open Terminal |

### Native Features (Built-in)
- **Web Search**: SearXNG, Google, Tavily
- **URL Fetching**: Extract text from websites
- **Image Generation**: DALL-E, ComfyUI, Automatic1111
- **Memory**: Remember facts across chats
- **RAG (Knowledge)**: Query uploaded documents

### Workspace Tools (Custom Plugins)
Python scripts running in Open WebUI. Can do anything Python can do. Only trusted admins should access.

### MCP (Model Context Protocol)
- **Native HTTP MCP**: Direct connection to MCP servers with HTTP/SSE endpoints.
- **MCPO (Proxy)**: Bridge for stdio-based MCP servers.

### OpenAPI / Function Calling Servers
Web servers with OpenAPI spec. Open WebUI ingests specs and treats endpoints as tools.

## How to Install Workspace Tools

1. Go to Community Tool Library (openwebui.com/search)
2. Choose a Tool, click **Get**
3. Enter Open WebUI instance URL
4. Click **Import to WebUI**

## How to Use Tools in Chat

**Option 1: On-the-fly** -- Click the **+** icon in the input area.
**Option 2: By Default** -- Go to **Workspace > Models**, edit model, check desired Tools in the Tools section.

Attached tools still require user read access. Users without read access to a tool won't see it even if attached to a model.

## Tool Calling Modes

### Default Mode (Legacy, Prompt-based)
- Works with practically any model
- Breaks KV cache, slower
- Does not support built-in system tools

### Native Mode (Agentic Mode) -- Recommended
- Leverages model's built-in tool-calling capabilities
- KV cache friendly, lower latency
- Supports multi-step chaining and autonomous decision-making
- Unlocks built-in system tools

**Enable**: Admin Panel > Settings > Models > Advanced Parameters > Function Calling > `Native`
Or per-chat: Chat Controls > Advanced Params > Function Calling > `Native`

| Feature | Default Mode | Native Mode |
|:---|:---|:---|
| **Status** | Legacy | Recommended |
| **Latency** | Medium/High | Low |
| **KV Cache** | Breaks cache | Cache-friendly |
| **System Tools** | Not available | Full access |
| **Complex Chaining** | Limited | Excellent |

### Built-in System Tools (Native Mode)

| Tool | Purpose |
|------|---------|
| `search_web` | Search the public web (requires ENABLE_WEB_SEARCH + per-chat toggle) |
| `fetch_url` | Visit URL and extract text content |
| `list_knowledge` | List attached knowledge (KBs, files, notes) |
| `list_knowledge_bases` | List accessible knowledge bases |
| `query_knowledge_files` | Semantic search over KB file contents |
| `search_knowledge_files` | Search files by filename |
| `view_file` | Read a file by ID with pagination |
| `view_knowledge_file` | Read a knowledge-base file by ID |
| `generate_image` | Generate image from prompt |
| `edit_image` | Edit existing images |
| `execute_code` | Execute code in sandboxed environment |
| `search_memories` | Search user's memory bank |
| `add_memory` | Store a new fact |
| `replace_memory_content` | Update existing memory |
| `delete_memory` | Delete a memory |
| `list_memories` | List all stored memories |
| `search_notes` | Search notes by title/content |
| `view_note` | Get full markdown content of a note |
| `write_note` | Create a new private note |
| `replace_note_content` | Update a note's content/title |
| `search_chats` | Text search across chat history |
| `view_chat` | Read full message history of a chat |
| `search_channels` | Find channels by name/description |
| `search_channel_messages` | Search messages in channels |
| `view_channel_message` | View a specific channel message |
| `view_channel_thread` | View a full thread in a channel |
| `view_skill` | Load full instructions of a skill |
| `get_current_timestamp` | Get current UTC timestamp and ISO date |
| `calculate_timestamp` | Calculate relative timestamps |

### Knowledge Tool Availability

| Tool | Model has attached knowledge | Model has no attached knowledge |
|------|------------------------------|---------------------------------|
| `list_knowledge` | Yes | No |
| `list_knowledge_bases` | No | Yes |
| `search_knowledge_files` | Yes (auto-scoped) | Yes (all accessible KBs) |
| `query_knowledge_files` | Yes (auto-scoped) | Yes |

`list_knowledge` and `list_knowledge_bases` are mutually exclusive.

### Interleaved Thinking (Native Mode)

Models follow a Thought-Action-Thought-Action loop: Reason > Act (call tool) > Think (evaluate) > Iterate > Finalize. Transforms chatbot into Agentic AI for complex multi-step problems.
