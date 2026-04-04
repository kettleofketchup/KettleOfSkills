# Multi-Model Chats

Open WebUI allows you to interact with **multiple models simultaneously** within a single chat interface. This powerful feature enables you to compare responses, verify facts, and leverage the unique strengths of different LLMs side-by-side.

## Overview

In a Multi-Model Chat, your prompt is sent to two or more selected models at the same time. Their responses are displayed in parallel columns (or stacked, depending on screen size), giving you immediate insight into how different AI architectures approach the same problem.

## How to Use

1. **Select Models**: In the chat header (Model Selector), click the **+ (Plus)** button to add more models to your current session.
   - *Example Setup*: Select **GPT-5.1 Thinking** (for reasoning), **Gemini 3** (for creative writing), and **Claude Sonnet 4.5** (for overall performance).
2. **Send Prompt**: Type your question as usual.
3. **View Results**: Watch as all models generate their responses simultaneously in the chat window.

## Usage Scenarios

- **Model Comparison/Benchmarking**: Test which model writes better Python code or which one hallucinates less on niche topics.
- **Fact Validation**: "Cross-examine" models. If two models say X and one says Y, you can investigate further.
- **Diverse Perspectives**: Get a "Creative" take from one model and a "Technical" take from another for the same query.

## Permissions

Admins can control access to Multi-Model Chats on a per-role or per-group basis.

- **Location**: Admin Panel > Settings > General > User Permissions > Chat > **Multiple Models**
- **Environment Variable**: `USER_PERMISSIONS_CHAT_MULTIPLE_MODELS` (Default: `True`)

If disabled, users will not see the "plus" button in the model selector and cannot initiate multi-model sessions.

## Merging Responses (Mixture of Agents)

Once you have responses from multiple models, Open WebUI offers an advanced capability to **Merge** them into a single, superior answer. This implements a **Mixture of Agents (MOA)** workflow.

### What is Merging?

Merging takes the outputs from all your active models and sends them -- along with your original prompt -- to a "Synthesizer Model." This Synthesizer Model reads all the draft answers and combines them into one final, polished response.

### How to Merge

1. Start a **Multi-Model Chat** and get responses from your selected models.
2. Look for the **Merge** (or "Synthesize") button in the response controls area (often near the regeneration controls).
3. Open WebUI will generate a **new response** that aggregates the best parts of the previous outputs.

### Advantages of Merging

- **Higher Accuracy**: Research suggests that aggregating outputs from multiple models often outperforms any single model acting alone.
- **Best of Both Worlds**: You might get the code accuracy of Model A combined with the clear explanations of Model B.
- **Reduced Hallucinations**: The synthesizer model can filter out inconsistencies found in individual responses.

### Configuration

The merging process relies on the backend **Tasks** system.

- **Task Model**: The specific model used to perform the merger can be configured in **Admin Panel > Settings > Tasks**. We recommend using a highly capable model (like GPT-5.1 or Claude Sonnet 4.5) as the task model for the best results.
- **Prompt Template**: The system uses a specialized prompt template to instruct the AI on how to synthesize the answers.

The Merging/MOA feature is an advanced capability. While powerful, it requires a capable Task Model to work effectively.

---

# Folders & Projects

Open WebUI provides powerful folder-based organization that turns simple chat containers into full-featured **project workspaces**. Folders allow you to not only group related conversations but also define specific contexts, system prompts, and knowledge bases that apply to all chats within them.

## Enabling Folders

Folders are enabled by default. Administrators can control this feature via:

- **Admin Panel**: The folders feature is controlled globally alongside other features.
- **Environment Variable**: `ENABLE_FOLDERS` - Set to `True` (default) to enable or `False` to disable.

## Core Features

### Creating Folders

Create a new folder to organize your conversations:

1. In the **sidebar**, click the **+ button** next to "Chats" or right-click in the chat list.
2. Select **"New Folder"**.
3. Enter a name for your folder.
4. Click **Save**.

### Moving Conversations into Folders

Organize existing chats by moving them into folders:

- **Drag and Drop**: Click and drag any conversation from the sidebar into a folder.
- **Right-click Menu**: Right-click on a conversation and select "Move to Folder".

### Nested Folders

Folders can be nested within other folders to create hierarchical organization:

- **Create subfolder from menu**: Right-click (or click the three-dot menu) on any folder and select **"Create Folder"** to create a new subfolder directly inside it.
- **Drag and drop**: Drag a folder onto another folder to make it a subfolder.
- **Move via context menu**: Right-click on a folder and use the move option to relocate it under a different parent.
- Folders can be expanded or collapsed to show/hide their contents.
- Subfolder names must be unique within the same parent folder. If a duplicate name is entered, a number is automatically appended (e.g., "Notes 1").

### Starting a Chat in a Folder

When you click on a folder in the sidebar, it becomes your **active workspace**:

1. Click on any folder in the sidebar to select it.
2. The chat interface will show that folder is active.
3. Any new chat you start will automatically be created inside this folder.
4. New chats will **inherit the folder's settings** (system prompt and knowledge).

## Folder Settings (Project Configuration)

Folders can be configured as full project workspaces with their own AI behavior and context. To edit folder settings:

1. Hover over a folder in the sidebar.
2. Click the **three-dot menu**.
3. Select **"Edit"** to open the folder settings modal.

### Folder Name

Change the name of your folder to better reflect its purpose or project.

### Folder Background Image

Customize the visual appearance of your folder by uploading a background image.

### System Prompt

Assign a dedicated **System Prompt** to the folder that automatically applies to all conversations within it:

- The system prompt is **prepended to every new conversation** created in the folder.
- This tailors the AI's behavior for specific tasks or personas.
- System prompts are optional -- you can use folders purely for organization without one.

The System Prompt field is only visible if you have permission to set system prompts (controlled by admin settings).

### Attached Knowledge

Link **knowledge bases and files** to your folder:

- All attached files and knowledge bases are automatically included as **context** for every chat in the folder.
- This enables RAG (Retrieval Augmented Generation) for all folder conversations.
- Knowledge is optional -- folders work for organization without any attached files.

## Tags (Complementary Organization)

In addition to folders, **tags** provide a flexible labeling system for conversations:

- **Adding Tags**: Apply keyword labels to conversations based on content or purpose.
- **Searching by Tags**: Filter conversations by tags using the search feature.
- **Flexible Organization**: Tags can be added or removed at any time and don't affect folder structure.

## Related Configuration

| Setting | Description |
|---------|-------------|
| `ENABLE_FOLDERS` | Enable/disable the folders feature globally (Default: `True`) |
| `USER_PERMISSIONS_FEATURES_FOLDERS` | Control user-level access to the folders feature (Default: `True`) |

