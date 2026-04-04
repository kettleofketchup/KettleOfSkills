# Agentic Web Search & URL Fetching

Open WebUI's web search has evolved from simple result injection to a fully **agentic research system**. By enabling **Native Function Calling (Agentic Mode)**, you allow quality models to independently explore the web, verify facts, and follow links autonomously.

Agentic web search works best with frontier models like **GPT-5**, **Claude 4.5+**, **Gemini 3+**, or **MiniMax M2.5** that can reason about search results and decide when to dig deeper. Small local models may struggle with the multi-step reasoning required.

## Native Mode vs. Traditional RAG

| Feature | Traditional RAG (Default) | Agentic Search (Native Mode) |
|---------|---------------------------|------------------------------|
| **Search Decision** | Open WebUI decides based on prompt analysis. | The **Model** decides if and when it needs to search. |
| **Data Processing** | Fetches ALL results, chunks them, and performs **RAG**. | Returns **Snippets** directly; no chunking or Vector DB. |
| **Link Following** | Snippets from top results are injected. | Model uses `fetch_url` to read a **Full Page** directly. |
| **Model Context** | Only gets relevant fragments (Top-K chunks). | Gets the **whole text** (up to ~50k chars) via `fetch_url`. |
| **Reasoning** | Model processes data *after* system injection. | Model can search, read, check, and search again. |

## How to Enable Agentic Behavior

To unlock these features, your model must support native tool calling and have strong reasoning capabilities (e.g., GPT-5, Claude 4.5 Sonnet, Gemini 3 Flash, MiniMax M2.5).

1. **Enable Web Search Globally**: Ensure a search engine is configured in **Admin Panel > Settings > Web Search**.
2. **Enable Model Capability**: In **Admin Panel > Settings > Models**, select your model and enable the **Web Search** capability.
3. **Enable Default Feature**: In the same model settings, under **Default Features**, check **Web Search**. This controls whether the `search_web` and `fetch_url` tools are available by default in new chat sessions.
4. **Enable Native Mode (Agentic Mode)**: In the same model settings, under **Advanced Parameters**, set **Function Calling** to `Native`.
5. **Use a Quality Model**: Ensure you're using a frontier model with strong reasoning capabilities for best results.

**Model Capability, Default Features, and Chat Toggle:** In **Native Mode**, the `search_web` and `fetch_url` tools require both the **Web Search** capability to be enabled *and* **Web Search** to be checked under **Default Features** in the model settings (or toggled on in the chat). If either is missing, the tools will not be injected -- even though other builtin tools may still appear.

In **Default Mode** (non-native), the chat toggle controls whether web search is performed via RAG-style injection.

**Important**: If you disable the `web_search` capability on a model but use Native Mode, the tools won't be available even if you manually toggle Web Search on in the chat.

## How Native Tools Handle Data (Agentic Mode)

Native Mode (Agentic Mode) works fundamentally differently from the global "Web Search" toggle found in standard models.

### `search_web` (Snippets only)

When the model invokes `search_web`:
- **Action**: It queries your search engine and receives a list of titles, links, and snippets.
- **No RAG**: Unlike traditional search, **no data is stored in a Vector DB**. No chunking or embedding occurs.
- **Result**: The model sees exactly what a human sees on a search results page. If the snippet contains the answer, the model responds. If not, the model must decide to "deep dive" into a link.

### `fetch_url` (Full Page Context)

If the model determines that a search snippet is insufficient, it will call `fetch_url`:
- **Direct Access**: The tool visits the specific URL and extracts the main text using your configured **Web Loader**.
- **Raw Context**: The extracted text is injected **directly into the model's context window** (hard-coded truncation at exactly 50,000 characters to prevent context overflow).
- **Agentic Advantage**: Because it doesn't use RAG, the model has the "full picture" of the page rather than isolated fragments. This allows it to follow complex instructions on specific pages (e.g., "Summarize the technical specifications table from this documentation link").

By keeping `search_web` and `fetch_url` separate and RAG-free, the model acts as its own **Information Retrieval** agent, choosing exactly which sources are worth reading in full.

## Deep Research & Interleaved Thinking

Because the model can call `search_web` multiple times and decide autonomously when to dive deeper, it can perform genuine "Deep Research" using **Interleaved Thinking**. This creates a powerful research loop where the model acts as its own research assistant.

### How Interleaved Thinking Works

Interleaved Thinking is the ability for models to alternate between **reasoning** and **action** in a continuous cycle. Instead of searching once and answering, the model can:

**Detailed Research Cycle Example:**

**User asks:** "What are the latest security vulnerabilities in the React ecosystem?"

**Step 1: Initial Analysis** - Model thinks: "I need current information about React security. Let me start with a broad search."

**Step 2: First Search**
```
Model calls: search_web("React security vulnerabilities 2026")
```
- Receives snippets from 5-10 search results
- Sees references to npm packages and CVE databases

**Step 3: Gap Analysis** - Model thinks: "The snippets mention CVEs but don't have enough detail. I should fetch a specific security advisory page."

**Step 4: Targeted Fetch**
```
Model calls: fetch_url("https://example.com/react-security-advisory-2026")
```
- Reads full 50k characters of detailed security documentation
- Identifies specific vulnerability types (XSS, injection, etc.)

**Step 5: Refinement** - Model thinks: "I found server-side vulnerabilities. Let me search specifically for client-side issues."

**Step 6: Refined Search**
```
Model calls: search_web("React client-side XSS CVE 2026")
```
- Gets more specific results about cross-site scripting issues
- Identifies mitigation strategies

**Step 7: Synthesis** - Model thinks: "I now have comprehensive information from multiple authoritative sources. Time to synthesize."

**Step 8: Final Answer** - Provides detailed, grounded response citing multiple sources, includes specific CVE numbers, affected versions, and mitigation steps.

### The Agentic Research Loop

The model continuously cycles through these phases until it has sufficient information:

1. **THINK**: Analyze current knowledge gaps and determine what information is missing
2. **ACT**: Search the web or fetch specific URLs to gather relevant content
3. **EVALUATE**: Assess the quality and completeness of the information retrieved
4. **DECIDE**: Determine if more research is needed or if enough context has been gathered
5. **ITERATE**: If gaps remain, return to step 1 with refined focus and more specific queries
6. **SYNTHESIZE**: Once sufficient information is gathered, compile and present the final answer

This cycle repeats autonomously until the model has comprehensive, verified information to answer your question with high confidence.

### Key Advantages

**Adaptive Precision**: The model doesn't just search once and accept whatever results appear. Instead, it continuously refines its search strategy based on what it discovers. If initial broad searches return surface-level information, the model automatically pivots to more specific technical terms, product names, version numbers, or specialized terminology.

**Deep Link Following & Discovery**: Unlike traditional RAG systems that only use search result snippets, the model can read full pages when snippets aren't sufficient. Even more powerfully, **when the model uses `fetch_url` to read a page, it can discover and follow new URLs mentioned within that content**. This creates a natural "web browsing" behavior where the model follows citation chains, explores linked resources, and builds a comprehensive understanding by reading multiple interconnected sources.

**Fact Verification & Cross-Referencing**: The model can autonomously verify information by cross-referencing multiple independent sources. This multi-source verification significantly reduces hallucination and increases answer reliability.

**Intelligent Gap Filling**: If initial search results miss key information or only partially address the question, the model identifies these gaps and automatically conducts follow-up searches with different terms, alternative phrasings, or more specific queries.

**Multi-Source Synthesis**: The model synthesizes insights from multiple web pages, documentation sites, forums, and articles into a coherent, well-rounded answer.

**Context-Aware Source Selection**: The model intelligently decides whether to rely on search snippets (when they contain sufficient information) or to fetch full pages (when deeper detail is needed).

## Save Search Results to Knowledge

The **Add Web Sources to Knowledge Action** allows you to save web search result URLs directly to your Knowledge Base with a single click. This feature streamlines the process of building a research bank by automating the fetching, sanitizing, and uploading of web content.

### Features

- **One-Click Saving**: Quickly add selected sources from a chat message to any Knowledge Base.
- **URL Selection**: Choose specific URLs to save from a numbered list.
- **Batch Processing**: Handle multiple URLs in a single action.
- **Duplicate Detection**: Automatically skip URLs that already exist in the target Knowledge Base.
- **Configurable Defaults**: Set a default Knowledge Base and skip confirmation dialogs for a faster workflow.

### Setup

The "Add Web Sources to Knowledge" feature is implemented as a **Function Action**. To use it:

1. **Download the Action**: Visit the Open WebUI Community Hub and download the [Add Web Sources to Knowledge Action](https://openwebui.com/posts/65d97417-d079-4720-b2cc-a63dd59b7e3e).
2. **Enable the Action**: Navigate to **Workspace > Functions**. Import or create a new function with the provided code. Enable the action globally or for specific models.

### How to Use

1. **Trigger Web Search**: Ask a question that triggers web search (e.g., using DDGS, Google PSE, etc.).
2. **Click the Action Button**: Once the model returns citations, click the **folder+** icon in the message toolbar.
3. **Select Sources**: A dialog will appear. Enter the numbers of the sources you wish to save (e.g., `1,3,5` or `1-3` or `all`).
4. **Choose Knowledge Base**: Select the target Knowledge Base where the content should be saved.
5. **Done**: The system will fetch the content using your configured **Web Loader** and add it to the Knowledge Base.

### Configuration (Valves)

You can customize the action's behavior through **Valves** in the function settings.

#### Admin Settings (Global Defaults)

| Setting | Default | Description |
|---------|---------|-------------|
| `max_urls_per_action` | `10` | Maximum number of URLs to process in a single action. |
| `enable_duplicate_check` | `True` | Check if URL already exists in the Knowledge Base before adding. |
| `default_knowledge_base` | `""` | System-wide default Knowledge Base name or ID. |
| `skip_confirmation` | `False` | Skip confirmation dialogs and use the default Knowledge Base. |
| `file_name_prefix` | `""` | Prefix for generated file names (e.g., `web_`). |

#### User Settings (Personal Overrides)

Users can override global defaults in their own settings:
- **Default Knowledge Base**: Set a preferred KB to avoid manual selection.
- **Skip Confirmation**: Enable for instant one-click saving (requires a default KB).
- **File Name Prefix**: Customize the prefix for your saved sources.

Set your **Default Knowledge Base** and enable **Skip Confirmation** in your User Valves to achieve instant, one-click saving of web sources.

### Troubleshooting

- **Content Quality**: The quality of the saved content depends on your **Web Loader Engine** settings (Admin > Settings > Documents). For JavaScript-heavy sites, consider using **Firecrawl** or **Playwright**.
- **No URLs Found**: This action works with web search results that return structured citations. If no URLs are detected, ensure web search is properly enabled and returning results.
