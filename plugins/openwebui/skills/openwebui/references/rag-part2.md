# RAG - Embedding, Re-indexing, Citations, and Advanced Features

## RAG Embedding Support

Change the RAG embedding model directly in the `Admin Panel` > `Settings` > `Documents` menu. This feature supports Ollama and OpenAI models, enabling you to enhance document processing according to your requirements.

## Changing RAG Settings After Initial Setup

If you need to change your chunking configuration (chunk size, overlap) or embedding model after documents have already been indexed, it is important to understand what actions are required and what effects those changes will have.

### Changing Chunk Size and Overlap

New documents will **automatically** use the updated chunk size and overlap settings -- no action is required for newly uploaded files.

Existing documents in knowledge bases **retain their original chunking** until you run a re-index. Retrieval will still work for these old chunks (vector similarity search does not depend on chunk size), but you may notice inconsistent retrieval quality if old and new documents have very different chunk sizes.

If you are only changing chunk settings and not the embedding model, a re-index is not strictly required -- old documents will continue to work. However, for consistent retrieval quality across all documents, running a re-index is recommended.

### Changing the Embedding Model

Changing the embedding model **requires a re-index** of all knowledge base documents. Embeddings from different models exist in different vector spaces and are not compatible with each other. Without re-indexing, retrieval against old embeddings will produce poor or nonsensical results.

After changing the embedding model in `Admin Panel` > `Settings` > `Documents`, navigate to `Admin Panel` > `Settings` > `Documents` and click the **Reindex** button to re-embed all knowledge base documents with the new model.

### What Does Re-Indexing Do?

The re-index process performs the following steps for each knowledge base:

1. **Deletes** the existing vector collection for the knowledge base.
2. **Re-chunks** all files using the current chunk size, overlap, and text splitter settings.
3. **Re-embeds** all chunks using the currently configured embedding model.

This means a single re-index applies both chunking setting changes and embedding model changes simultaneously.

**Warning:** The re-index operation only processes files that belong to **knowledge bases**. Files that were uploaded directly into a chat (without being added to a knowledge base) have their own per-file vector collections that are not touched by re-indexing. If you change the embedding model, those standalone chat file embeddings will still use the old model and retrieval quality for those files will degrade. The only way to update them is to re-upload the files.

### Summary

| Change | New Documents | Knowledge Base Documents (no re-index) | Knowledge Base Documents (after re-index) | Standalone Chat Files |
|---|---|---|---|---|
| **Chunk Size / Overlap** | Uses new settings | Old chunks still work, but quality may vary | Re-chunked with new settings | Old chunks, re-upload to update |
| **Embedding Model** | Uses new model | Old embeddings, incompatible vector space | Re-embedded with new model | Old embeddings, re-upload to update |

## Citations in RAG Feature

The RAG feature allows users to easily track the context of documents fed to LLMs with added citations for reference points. This ensures transparency and accountability in the use of external sources within your chats.

## File Context vs Builtin Tools

Open WebUI provides two separate capabilities that control how files are handled. Understanding the difference is important for configuring models correctly.

### File Context Capability

The **File Context** capability controls whether Open WebUI performs RAG (Retrieval-Augmented Generation) on attached files:

| File Context | Behavior |
|--------------|----------|
| **Enabled** (default) | Attached files are processed via RAG. Content is retrieved and injected into the conversation context. |
| **Disabled** | File processing is **completely skipped**. No content extraction, no injection. The model receives no file content. |

**When to disable File Context:**
- **Bypassing RAG entirely**: When you don't want Open WebUI to process attached files at all.
- **Using Builtin Tools only**: If you prefer the model to retrieve file content on-demand via tools like `query_knowledge_bases` rather than having content pre-injected.
- **Debugging/testing**: To isolate whether issues are related to RAG processing.

**Warning:** When File Context is disabled, file content is **not automatically extracted or injected**. Open WebUI does not forward files to the model's native API. If you disable this, the only way the model can access file content is through builtin tools (if enabled) that query knowledge bases or retrieve attached files on-demand (agentic file processing).

Individual files and knowledge bases can also be set to bypass RAG entirely using the **"Using Entire Document"** toggle. This injects the full file content into every message regardless of native function calling settings.

The File Context toggle only appears when **File Upload** is enabled for the model.

### Builtin Tools Capability

The **Builtin Tools** capability controls whether the model receives native function-calling tools for autonomous retrieval:

| Builtin Tools | Behavior |
|---------------|----------|
| **Enabled** (default) | In Native Function Calling mode, the model receives tools like `query_knowledge_bases`, `view_knowledge_file`, `search_chats`, etc. |
| **Disabled** | No builtin tools are injected. The model works only with pre-injected context. |

**When to disable Builtin Tools:**
- **Model doesn't support function calling**: Smaller or older models may not handle the `tools` parameter.
- **Predictable behavior needed**: You want the model to work only with what's provided upfront.

### Combining the Two Capabilities

These capabilities work independently, giving you fine-grained control:

| File Context | Builtin Tools | Result |
|--------------|---------------|--------|
| Enabled | Enabled | **Full Agentic Mode**: RAG content injected + model can autonomously query knowledge bases |
| Enabled | Disabled | **Traditional RAG**: Content injected upfront, no autonomous retrieval tools |
| Disabled | Enabled | **Tools-Only Mode**: No pre-injected content, but model can use tools to query knowledge bases or retrieve attached files on-demand |
| Disabled | Disabled | **No File Processing**: Attached files are ignored, no content reaches the model |

**Choosing the Right Configuration:**
- **Most models**: Keep both enabled (defaults) for full functionality.
- **Small/local models**: Disable Builtin Tools if they don't support function calling.
- **On-demand retrieval only**: Disable File Context, enable Builtin Tools if you want the model to decide what to retrieve rather than pre-injecting everything.

## Enhanced RAG Pipeline

The togglable hybrid search sub-feature for our RAG embedding feature enhances RAG functionality via `BM25`, with re-ranking powered by `CrossEncoder`, and configurable relevance score thresholds. This provides a more precise and tailored RAG experience for your specific use case.

## KV Cache Optimization (Performance Tip)

For professional and high-performance use cases -- especially when dealing with long documents or frequent follow-up questions -- you can significantly improve response times by enabling **KV Cache Optimization**.

### The Problem: Cache Invalidation

By default, Open WebUI injects retrieved RAG context into the **user message**. As the conversation progresses, follow-up messages shift the position of this context in the chat history. For many LLM engines -- including local engines (like Ollama, llama.cpp, and vLLM) and cloud providers / Model-as-a-Service providers (like OpenAI and Vertex AI) -- this shifting position invalidates the **KV (Key-Value) prefix cache** or **Prompt Cache**, forcing the model to re-process the entire context for every single response. This leads to increased latency and potentially higher costs as the conversation grows.

### The Solution: `RAG_SYSTEM_CONTEXT`

You can fix this behavior by enabling the `RAG_SYSTEM_CONTEXT` environment variable.

- **How it works**: When `RAG_SYSTEM_CONTEXT=True`, Open WebUI injects the RAG context into the **system message** instead of the user message.
- **The Result**: Since the system message stays at the absolute beginning of the prompt and its position never changes, the provider can effectively cache the processed context. Follow-up questions then benefit from **instant responses** and **cost savings** because the "heavy lifting" (processing the large RAG context) is only done once.

If you are using **Ollama**, **llama.cpp**, **OpenAI**, or **Vertex AI** and frequently "chat with your documents," set `RAG_SYSTEM_CONTEXT=True` in your environment to experience drastically faster follow-up responses.

## YouTube RAG Pipeline

The dedicated RAG pipeline for summarizing YouTube videos via video URLs enables smooth interaction with video transcriptions directly. This innovative feature allows you to incorporate video content into your chats, further enriching your conversation experience.

## Document Parsing

A variety of parsers extract content from local and remote documents. For more, see the [`get_loader`](https://github.com/open-webui/open-webui/blob/2fa94956f4e500bf5c42263124c758d8613ee05e/backend/apps/rag/main.py#L328) function.

**Warning:** When using **Temporary Chat**, document processing is restricted to **frontend-only** operations to ensure your data stays private and is not stored on the server. Consequently, advanced backend parsing (used for formats like complex DOCX files) is disabled, which may result in raw data being seen instead of parsed text. For full document support, use a standard chat session.

## Google Drive Integration

When paired with a Google Cloud project that has the Google Picker API and Google Drive API enabled, this feature allows users to directly access their Drive files from the chat interface and upload documents, slides, sheets and more and uploads them as context to your chat. Can be enabled `Admin Panel` > `Settings` > `Documents` menu. Must set `GOOGLE_DRIVE_API_KEY` and `GOOGLE_DRIVE_CLIENT_ID` environment variables to use.

### Detailed Instructions

1. Create an OAuth 2.0 client and configure both the Authorized JavaScript origins & Authorized redirect URI to be the URL (include the port if any) you use to access your Open-WebUI instance.
2. Make a note of the Client ID associated with that OAuth client.
3. Make sure that you enable both Google Drive API and Google Picker API for your project.
4. Also set your app (project) as Testing and add your Google Drive email to the User List
5. Set the permission scope to include everything those APIs have to offer. And because the app would be in Testing mode, no verification is required by Google to allow the app from accessing the data of the limited test users.
6. Go to the Google Picker API page, and click on the create credentials button.
7. Create an API key and under Application restrictions and choose Websites. Then add your Open-WebUI instance's URL, same as the Authorized JavaScript origins and Authorized redirect URIs settings in the step 1.
8. Set up API restrictions on the API Key to only have access to Google Drive API & Google Picker API
9. Set up the environment variable, `GOOGLE_DRIVE_CLIENT_ID` to the Client ID of the OAuth client from step 2.
10. Set up the environment variable `GOOGLE_DRIVE_API_KEY` to the API Key value setup up in step 7 (NOT the OAuth client secret from step 2).
11. Set up the `GOOGLE_REDIRECT_URI` to my Open-WebUI instance's URL (include the port, if any).
12. Then relaunch your Open-WebUI instance with those three environment variables.
13. After that, make sure Google Drive was enabled under `Admin Panel` > `Settings` > `Documents` > `Google Drive`
