# Memory & Personalization

The Memory system is currently in **Beta/Experimental** stage. You may encounter inconsistencies in how models store or retrieve information, and storage formats may change in future updates.

Open WebUI includes a sophisticated memory system that allows models to remember facts, preferences, and context across different conversations. With the introduction of **Native Tool Calling**, this system has been upgraded from a passive injection mechanism to an active, model-managed "long-term memory."

## How it Works

The memory system stores snippets of information about you (e.g., "I prefer Python for backend tasks" or "I live in Vienna"). There are two ways these memories are used:

### 1. Manual Management (Settings)

Users can manually add, edit, or delete memories by navigating to:
**Settings > Personalization > Memory**

### 2. Native Memory Tools (Agentic Mode)

When using a model with **Native Function Calling (Agentic Mode)** enabled, quality models can manage your memory autonomously using five built-in tools.

Autonomous memory management works best with frontier models (GPT-5, Claude 4.5+, Gemini 3+) that can intelligently decide what facts are worth saving and when to recall relevant memories. Small local models may struggle with appropriate memory selection.

- **`add_memory`**: Allows the model to proactively save a new fact it learned about you during the conversation.
- **`search_memories`**: Allows the model to search your memory bank for relevant context. Results include a unique `id` for each memory snippet. The model can optionally specify how many memories to return (default is 5).
- **`replace_memory_content`**: Allows the model to update or correct a specific existing memory using its `id`.
- **`delete_memory`**: Allows the model to remove a memory that is no longer relevant or correct, using its `id`.
- **`list_memories`**: Allows the model to retrieve all stored memories for the user, including content and timestamps.

## Benefits of the Memory System

- **Proactive Learning**: Instead of you manually typing preferences, a model can say: *"I'll remember that you prefer dark mode for your UI projects"* and call `add_memory` behind the scenes.
- **Contextual Retrieval**: If a conversation drifts into a topic mentioned months ago, the model can "search its brain" using `search_memories` to find those past details.
- **Dynamic Correction**: If the model remembers something incorrectly, it can use `replace_memory_content` to fix the fact rather than creating a duplicate.
- **Cleanup**: The model can use `delete_memory` to remove outdated or irrelevant facts, keeping your memory bank clean.
- **Full Visibility**: Using `list_memories`, the model can review everything it knows about you and identify gaps or contradictions.
- **User Control**: Even though models can add memories, users retain full control. Every memory added by a model can be reviewed and deleted in the Personalization settings.

## Enabling Memory Tools

1. **Administrative Enablement**: Ensure the Memory feature is enabled globally by an administrator and that you have the required permissions.
2. **Native Mode (Agentic Mode)**: Enable **Native Function Calling** in the model's advanced parameters (**Admin Panel > Settings > Models > Model Specific Settings > Advanced Parameters**).
3. **Quality Models Required**: To unlock these features effectively, use frontier models with strong reasoning capabilities (e.g., GPT-5, Claude 4.5 Sonnet, Gemini 3 Flash, MiniMax M2.5) for the best experience. Small local models may not effectively manage memories autonomously.
4. **Per-Model Category Toggle**: Ensure the **Memory** category is enabled for the model in **Workspace > Models > Edit > Builtin Tools** (enabled by default).

## Administrative Controls

Administrators have full control over the Memory feature, including the ability to disable it globally or restrict it to specific user groups.

### Global Toggle
The Memory feature can be toggled on or off for the entire instance. When disabled, the "Personalization" tab is hidden from all users, and the memory-related API endpoints are blocked.
- **Admin UI**: Admin Panel > Settings > General > Features > **Memories**
- **Environment Variable**: `ENABLE_MEMORIES` (Default: `True`)

### Granular Permissions
Administrators can also control Memory access on a per-role or per-group basis from the Permissions interface.
- **Admin UI**: Admin Panel > Users > Permissions > Features > **Memories**
- **Environment Variable**: `USER_PERMISSIONS_FEATURES_MEMORIES` (Default: `True`)

## Privacy & Security

Memories are stored locally in your Open WebUI database and are specific to your user account. They are never shared across users, and you can clear your entire memory bank at any time.

---

# Direct Connections

This feature is currently **experimental** and may change or be removed in future releases.

**Direct Connections** is a feature that allows users to connect their Open WebUI client directly to OpenAI-compatible API endpoints, bypassing the Open WebUI backend for inference requests.

## Overview

In a standard deployment, Open WebUI acts as a proxy: the browser sends the prompt to the Open WebUI backend, which then forwards it to the LLM provider (Ollama, OpenAI, etc.).

With **Direct Connections**, the browser communicates directly with the API provider.

## Benefits

- **Privacy & Control**: Users can use their own personal API keys without storing them on the Open WebUI server (keys are stored in the browser's local storage).
- **Reduced Latency**: Removes the "middleman" hop through the Open WebUI backend, potentially speeding up response times.
- **Server Load Reduction**: Offloads the network traffic and connection management from the Open WebUI server to the individual client browsers.

## Prerequisites

1. **Admin Enablement**: The administrator must enable this feature globally.
   - **Admin Panel > Settings > Connections > Direct Connections**: Toggle **On**.
   - Alternatively, set the environment variable: `ENABLE_DIRECT_CONNECTIONS=true`.
2. **CORS Configuration**: Since the browser is making the request, the API provider must have **Cross-Origin Resource Sharing (CORS)** configured to allow requests from your Open WebUI domain.
   - Many strict providers (like official OpenAI) might block direct browser requests due to CORS policies. This feature is often best used with flexible providers or internal API gateways.

## User Configuration

Once enabled by the admin, users can configure their own connections:

1. Go to **User Settings > Connections**.
2. Click **+ (Add Connection)**.
3. Enter the **Base URL** (e.g., `https://api.groq.com/openai/v1`) and your **API Key**.
4. Click **Save**.

The models from this direct connection will now appear in your model list, often indistinguishable from backend-provided models, but requests will flow directly from your machine to the provider.
