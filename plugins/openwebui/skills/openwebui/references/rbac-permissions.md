# RBAC Permissions

Administrators manage permissions in two ways:
1. **Default Permissions:** Baseline for all users via **Admin Panel > Users > Groups > Default Permissions**
2. **Group Permissions:** Specific overrides via **Admin Panel > Users > Groups**

**Permission Logic:** Permissions are additive. True takes precedence over False. If any source (Global Default or any Group) grants a permission, the user will have it. To restrict a feature, it must be disabled globally AND in all groups the user belongs to.

**Best Practice:** Start with minimal Global Default Permissions, then grant via specific groups (Principle of Least Privilege).

## 1. Workspace Permissions

| Permission | Description |
|---|---|
| **Models Access** | (Parent) Access the Models workspace to create or edit custom models |
| **Models Import** | (Requires Models Access) Import models from JSON/files |
| **Models Export** | (Requires Models Access) Export models to files |
| **Knowledge Access** | Access the Knowledge workspace to manage knowledge bases |
| **Prompts Access** | (Parent) Access the Prompts workspace to manage custom system prompts |
| **Prompts Import** | (Requires Prompts Access) Import prompts |
| **Prompts Export** | (Requires Prompts Access) Export prompts |
| **Tools Access** | (Parent) Access the Tools workspace to manage functions/tools |
| **Tools Import** | (Requires Tools Access) Import tools |
| **Tools Export** | (Requires Tools Access) Export tools |
| **Skills Access** | Access the Skills workspace to create and manage reusable instruction sets |

**WARNING: Tools Access = Root-Equivalent Access.** Granting Tools Access is equivalent to giving shell access to your server because Tools and Functions execute arbitrary Python code. Only grant to trusted users.

## 2. Sharing Permissions

| Permission | Description |
|---|---|
| **Share Models** | (Parent) Share models with others |
| **Public Models** | (Requires Share Models) Make models publicly discoverable |
| **Share Knowledge** | (Parent) Share knowledge bases |
| **Public Knowledge** | (Requires Share Knowledge) Make knowledge bases public |
| **Share Prompts** | (Parent) Share prompts |
| **Public Prompts** | (Requires Share Prompts) Make prompts public |
| **Share Tools** | (Parent) Share tools |
| **Public Tools** | (Requires Share Tools) Make tools public |
| **Share Skills** | (Parent) Share skills |
| **Public Skills** | (Requires Share Skills) Make skills public |
| **Share Notes** | (Parent) Share Notes |
| **Public Notes** | (Requires Share Notes) Make Notes public |

## 3. Chat Permissions

| Permission | Description |
|---|---|
| **Chat Controls** | (Parent) Access to advanced chat settings. Required for Valves, System Prompt, and Parameters |
| **Model Valves** | (Requires Chat Controls) Model-specific configuration "valves" |
| **System Prompt** | (Requires Chat Controls) Edit the system prompt for a conversation |
| **Parameters** | (Requires Chat Controls) Adjust LLM parameters (temperature, top_k, etc.) |
| **File Upload** | Upload files to the chat |
| **Delete Chat** | Delete entire chat conversations |
| **Delete Message** | Delete individual messages |
| **Edit Message** | Edit messages |
| **Continue Response** | Use the "Continue" feature for truncated responses |
| **Regenerate Response** | Regenerate an AI response |
| **Rate Response** | Thumbs up/down responses |
| **Share Chat** | Generate a share link for a chat |
| **Export Chat** | Export chat history |
| **Speech-to-Text (STT)** | Voice input |
| **Text-to-Speech (TTS)** | Voice output |
| **Audio Call** | Real-time audio call feature |
| **Multiple Models** | Select multiple models for simultaneous response |
| **Temporary Chat** | (Parent) Toggle "Temporary Chat" (incognito mode/history off). Backend document parsing is disabled in this mode. |
| **Enforced Temporary** | (Requires Temporary Chat) Restricts user to always use temporary chat |

## 4. Features Permissions

| Permission | Description |
|---|---|
| **API Keys** | Non-admin users can generate Personal Access Tokens (API Keys) |
| **Notes** | Access to the Notes feature |
| **Channels** | Access to the Channels feature |
| **Folders** | Use folders for organizing chats |
| **Web Search** | Use Web Search integration |
| **Image Generation** | Use Image Generation tools |
| **Code Interpreter** | Use the Python Code Interpreter |
| **Direct Tool Servers** | Connect to custom Tool Servers in settings |
| **Memories** | Access to the Memories feature for persistent user context |

## 5. Settings Permissions

| Permission | Description |
|---|---|
| **Interface Settings Access** | Access and modify interface settings in user settings |

## API Keys Permission Scope

1. **Global Toggle Required**: Must be enabled in **Admin Settings > General > Enable API Keys**. When off, no one can generate keys.
2. **Permission Check for Non-Admins**: Users with `user` role need the `features.api_keys` permission.
3. **Admins Are Exempt**: Admin users can generate API keys when globally enabled, even without the specific permission.

## Environment Variables

Initial defaults can be set via environment variables (prefixed with `USER_PERMISSIONS_`):
- `ENABLE_IMAGE_GENERATION=True`
- `ENABLE_WEB_SEARCH=True`
- `USER_PERMISSIONS_CHAT_FILE_UPLOAD=True`

**Best Practice:** Create a dedicated "Administrators" group, add all admin users, and grant user-facing feature permissions to the group. This ensures consistent access when new permissions are added.
