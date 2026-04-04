# Chat Parameters

Within Open WebUI, there are three levels to setting a **System Prompt** and **Advanced Parameters**: per-chat basis, per-model basis, and per-account basis. This hierarchical system allows for flexibility while maintaining structured administration and control.

## System Prompt and Advanced Parameters Hierarchy Chart

| **Level** | **Definition** | **Modification Permissions** | **Override Capabilities** |
| --- | --- | --- | --- |
| **Per-Chat** | System prompt and advanced parameters for a specific chat instance | Users can modify, but cannot override model-specific settings | Restricted from overriding model-specific settings |
| **Per-Account** | Default system prompt and advanced parameters for a specific user account | Users can set, but may be overridden by model-specific settings | User settings can be overridden by model-specific settings |
| **Per-Model** | Default system prompt and advanced parameters for a specific model | Administrators can set, Users cannot modify | Admin-specific settings take precedence, User settings can be overridden |

### 1. Per-chat basis

- **Description**: The per-chat basis setting refers to the system prompt and advanced parameters configured for a specific chat instance. These settings are only applicable to the current conversation and do not affect future chats.
- **How to set**: Users can modify the system prompt and advanced parameters for a specific chat instance within the right-hand sidebar's **Chat Controls** section in Open WebUI.
- **Override capabilities**: Users are restricted from overriding the **System Prompt** or specific **Advanced Parameters** already set by an administrator on a per-model basis. This ensures consistency and adherence to model-specific settings.

**Example Use Case**: Suppose a user wants to set a custom system prompt for a specific conversation. They can do so by accessing the **Chat Controls** section and modifying the **System Prompt** field. These changes will only apply to the current chat session.

### 2. Per-account basis

- **Description**: The per-account basis setting refers to the default system prompt and advanced parameters configured for a specific user account. Any user-specific changes can serve as a fallback in situations where lower-level settings aren't defined.
- **How to set**: Users can set their own system prompt and advanced parameters for their account within the **General** section of the **Settings** menu in Open WebUI.
- **Override capabilities**: Users have the ability to set their own system prompt on their account, but they must be aware that such parameters can still be overridden if an administrator has already set the **System Prompt** or specific **Advanced Parameters** on a per-model basis for the particular model being used.

**Example Use Case**: Suppose a user wants to set their own system prompt for their account. They can do so by accessing the **Settings** menu and modifying the **System Prompt** field.

### 3. Per-model basis

- **Description**: The per-model basis setting refers to the default system prompt and advanced parameters configured for a specific model. These settings are applicable to all chat instances using that model.
- **How to set**: Administrators can set the default system prompt and advanced parameters for a specific model within the **Models** section of the **Workspace** in Open WebUI.
- **Override capabilities**: **User** accounts are restricted from modifying the **System Prompt** or specific **Advanced Parameters** on a per-model basis. This restriction prevents users from inappropriately altering default settings.
- **Context length preservation:** When a model's **System Prompt** or specific **Advanced Parameters** are set manually in the **Workspace** section by an Admin, said **System Prompt** or manually set **Advanced Parameters** cannot be overridden or adjusted on a per-account basis within the **General** settings or **Chat Controls** section by a **User** account. This ensures consistency and prevents excessive reloading of the model whenever a user's context length setting changes.
- **Model precedence:** If a model's **System Prompt** or specific **Advanced Parameters** value is pre-set in the Workspace section by an Admin, any context length changes made by a **User** account in the **General** settings or **Chat Controls** section will be disregarded, maintaining the pre-configured value for that model. Be advised that parameters left untouched by an **Admin** account can still be manually adjusted by a **User** account on a per-account or per-chat basis.

**Example Use Case**: Suppose an administrator wants to set a default system prompt for a specific model. They can do so by accessing the **Models** section and modifying the **System Prompt** field for the corresponding model. Any chat instances using this model will automatically use the model's system prompt and advanced parameters.

## Optimize System Prompt Settings for Maximum Flexibility

**This tip applies for both administrators and user accounts. To achieve maximum flexibility with your system prompts, we recommend considering the following setup:**

- Assign your primary System Prompt (**i.e., to give an LLM a defining character**) you want to use in your **General** settings **System Prompt** field. This sets it on a per-account level and allows it to work as the system prompt across all your LLMs without requiring adjustments within a model from the **Workspace** section.

- For your secondary System Prompt (**i.e, to give an LLM a task to perform**), choose whether to place it in the **System Prompt** field within the **Chat Controls** sidebar (on a per-chat basis) or the **Models** section of the **Workspace** section (on a per-model basis) for Admins, allowing you to set them directly. This allows your account-level system prompt to work in conjunction with either the per-chat level system prompt provided by **Chat Controls**, or the per-model level system prompt provided by **Models**.

- As an administrator, you should assign your LLM parameters on a per-model basis using **Models** section for optimal flexibility. For both of these secondary System Prompts, ensure to set them in a manner that maximizes flexibility and minimizes required adjustments across different per-account or per-chat instances. It is essential for both your Admin account as well as all User accounts to understand the priority order by which system prompts within **Chat Controls** and the **Models** section will be applied to the **LLM**.

---

# URL Parameters

In Open WebUI, chat sessions can be customized through various URL parameters. These parameters allow you to set specific configurations, enable features, and define model settings on a per-chat basis.

## URL Parameter Overview

| **Parameter** | **Description** | **Example** |
|---|---|---|
| `models` | Specifies the models to be used, as a comma-separated list. | `/?models=model1,model2` |
| `model` | Specifies a single model to be used for the chat session. | `/?model=model1` |
| `youtube` | Specifies a YouTube video ID to be transcribed within the chat. | `/?youtube=VIDEO_ID` |
| `load-url` | Specifies a Website URL to be fetched and uploaded as a document within the chat. | `/?load-url=https://google.com` |
| `web-search` | Enables web search functionality if set to `true`. | `/?web-search=true` |
| `tools` or `tool-ids` | Specifies a comma-separated list of tool IDs to activate in the chat. | `/?tools=tool1,tool2` |
| `call` | Enables a call overlay if set to `true`. | `/?call=true` |
| `q` | Sets an initial query or prompt for the chat. | `/?q=Hello%20there` |
| `temporary-chat` | Marks the chat as temporary if set to `true`, for one-time sessions. | `/?temporary-chat=true` |
| `code-interpreter` | Enables the code interpreter feature if set to `true`. | `/?code-interpreter=true` |
| `image-generation` | Enables the image generation feature if set to `true`. | `/?image-generation=true` |

### Models and Model Selection

The `models` and `model` parameters allow you to specify which language models should be used for a particular chat session. Use either `models` for multiple models or `model` for a single model.

- `/?models=model1,model2` -- initializes the chat with `model1` and `model2`.
- `/?model=model1` -- sets `model1` as the sole model for the chat.

### YouTube Transcription

The `youtube` parameter takes a YouTube video ID, enabling the chat to transcribe the specified video. Example: `/?youtube=VIDEO_ID`

### Website Insertion

The `load-url` parameter downloads the specified website and extracts the content to upload it as a document into the chat. Example: `/?load-url=https://google.com`

### Web Search

Enabling `web-search` allows the chat session to access web search functionality. Set to `true` to enable. Example: `/?web-search=true`

### Tool Selection

The `tools` or `tool-ids` parameters specify which tools to activate within the chat. Provide a comma-separated list of tool IDs. Example: `/?tools=tool1,tool2`

### Call Overlay

The `call` parameter enables a video or call overlay in the chat interface. Set to `true` to enable. Activates a call interface overlay, allowing features such as live transcription and video input.

### Initial Query Prompt

The `q` parameter allows setting an initial query or prompt for the chat. The chat starts with the specified prompt, automatically submitting it as the first message. Example: `/?q=Hello%20there`

### Temporary Chat Sessions

The `temporary-chat` parameter marks the chat as a temporary session. This limits features such as saving chat history or applying persistent settings. Set to `true` for a temporary chat session.

**Note**: Document processing in temporary chats is frontend-only for privacy. Complex files requiring backend parsing (e.g., DOCX) may not be fully supported.

### Code Interpreter

The `code-interpreter` parameter enables the code interpreter feature. Set to `true` to enable.

### Image Generation

The `image-generation` parameter enables the image generation for the provided prompt. Set to `true` to enable.

## Using Multiple Parameters Together

These URL parameters can be combined to create highly customized chat sessions. For example:

```
/?models=model1,model2&youtube=VIDEO_ID&web-search=true&tools=tool1,tool2&call=true&q=Hello%20there&temporary-chat=true
```

This URL will:
- Initialize the chat with `model1` and `model2`.
- Enable YouTube transcription, web search, and specified tools.
- Display a call overlay.
- Set an initial prompt of "Hello there."
- Mark the chat as temporary, avoiding any history saving.
