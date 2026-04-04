# Chat Sharing

## Enabling Community Sharing

To enable community sharing, follow these steps:

1. Navigate to the **Admin Panel** page as an **Admin**.
2. Click on the **Settings** tab.
3. Toggle on **Enable Community Sharing** within the **General** settings tab.

Only Admins can toggle the **Enable Community Sharing** option. If this option is toggled off, users and Admins will not see the **Share to Open WebUI Community** option for sharing their chats. Community sharing must be enabled by an Admin for users to share chats to the Open WebUI community.

This will enable community sharing for all users on your Open WebUI instance.

## Sharing Chats

To share a chat:

1. Select the chat conversation you want to share.
2. Click on the 3-dots that appear when hovering the mouse pointer above the desired chat.
3. Then click on the **Share** option.
4. Select either **Share to Open WebUI Community** (if **Enable Community Sharing** is toggled on by an **Admin**) or **Copy Link**.

### Sharing to Open WebUI Community

When you select `Share to Open WebUI Community`:

- A new tab will open, allowing you to upload your chat as a snapshot to the Open WebUI community website (https://openwebui.com/chats/upload).
- You can control who can view your uploaded chat by choosing from the following access settings:
  - **Private**: Only you can access this chat.
  - **Public**: Anyone on the internet can view the messages displayed in the chat snapshot.
  - **Public, Full History**: Anyone on the internet can view the full regeneration history of your chat.

You can change the permission level of your shared chats on the community platform at any time from your openwebui.com account.

**Currently, shared chats on the community website cannot be found through search. However, future updates are planned to allow public chats to be discoverable by the public if their permission is set to `Public` or `Public, Full History`.**

Example of a shared chat to the community platform website: https://openwebui.com/c/iamg30/5e3c569f-905e-4d68-a96d-8a99cc65c90f

### Copying a Share Link

When you select `Copy Link`, a unique share link is generated that can be shared with others.

**Important Considerations:**

- The shared chat will only include messages that existed at the time the link was created. Any new messages sent within the chat after the link is generated will not be included, unless the link is deleted and updated with a new link.
- The generated share link acts as a static snapshot of the chat at the time the link was generated.
- To view the shared chat, users must:
  1. Have an account on the Open WebUI instance where the link was generated.
  2. Be signed in to their account on that instance.
- If a user tries to access the shared link without being signed in, they will be redirected to the login page to log in before they can view the shared chat.

## Viewing Shared Chats

To view a shared chat:

1. Ensure you are signed in to an account on the Open WebUI instance where the chat was shared.
2. Click on the shared link provided to you.
3. The chat will be displayed in a read-only format.
4. If the Admin of the Open WebUI instance from which the shared link was shared has Text-to-Speech set up, there may be an audio button for messages to be read aloud to you (situational).

## Updating Shared Chats

To update a shared chat:

1. Select the chat conversation you want to share.
2. Click on the 3-dots that appear when hovering the mouse pointer above the desired chat.
3. Click on the **Share** option.
4. The **Share Chat** Modal should look different if you've shared a chat before.

The **Share Chat** Modal includes the following options:

- **before**: Opens a new tab to view the previously shared chat from the share link.
- **delete this link**: Deletes the shared link of the chat and presents the initial share chat modal.
- **Share to Open WebUI Community**: Opens a new tab for https://openwebui.com/chats/upload with the chat ready to be shared as a snapshot.
- **Update and Copy Link**: Updates the snapshot of the chat of the previously shared chat link and copies it to your device's clipboard.

## Deleting Shared Chats

To delete a shared chat link:

1. Select the chat conversation you want to delete the shared link for.
2. Click on the 3-dots that appear when hovering the mouse pointer above the desired chat.
3. Click on the **Share** option.
4. The **Share Chat** Modal should look different if you've shared a chat before.
5. Click on **delete this link**.

Once deleted, the shared link will no longer be valid, and users will not be able to view the shared chat.

Chats shared to the community platform cannot be deleted. To change the access level of a chat shared to the community platform:

1. Log in to your Open WebUI account on openwebui.com.
2. Click on your account username at the top right of the website.
3. Click on **Chats**.
4. Click on the chat you wish to change permission access for.
5. Scroll to the bottom of the chat and update its permission level.
6. Click the **Update Chat** button.

## Managing Shared Chats

Open WebUI provides a centralized dashboard to manage every chat conversation you have shared. From there you can search through your shared history, re-copy links, or revoke access instantly.

For details on the management dashboard, see the Shared Chats Management section under Data Controls.

---

# History & Search

Open WebUI provides a powerful system for managing and navigating your previous conversations.

## Chat History Sidebar

All your conversations are automatically saved in the **Sidebar**.

- **Persistence**: Chats are saved to the internal database (`webui.db`) and are available across all your devices.
- **Organization**: Chats are grouped by time period (Today, Yesterday, Previous 7 Days, etc.).
- **Renaming**: Titles are automatically generated by a task model, but you can manually rename any chat by clicking the pencil icon next to its title.
- **Archival**: Instead of deleting, you can **Archive** chats to remove them from the main list while keeping them downloadable and searchable.

## Searching Your History

You can search through your conversations using the global search bar in the sidebar.

1. Click the **Search** icon or use the keyboard shortcut `Cmd+K` / `Ctrl+K`.
2. Type your query. Open WebUI performs a fuzzy search across:
   - **Chat Titles**
   - **Message Content**
   - **Tags** (Search using `tag:my-tag-name`)
3. Click on a result to immediately jump to that conversation.

## Native Conversation Search (Agentic)

When using a model with **Native Function Calling** enabled, models can search through your chat history autonomously.

### Available History Tools:
- **`search_chats`**: Simple text search across chat titles and message content. Returns matching chat IDs and snippets.
- **`view_chat`**: Reads and returns the full message history of a specific chat by ID.

### Why use native tool calling for Search?
This allows the model to leverage its own previous work. You can ask: *"What was the feedback I got on my last email draft?"* or *"Find the Python script I wrote about image processing two weeks ago."*

The model will search your history, identify the correct chat, read it, and provide you with an answer or the code you were looking for.

## Data Management

- **Export**: You can download individual chats or your entire history as **JSON**, **PDF**, or **Markdown**.
- **Import**: Drag and drop a JSON chat export into the sidebar to restore it.
- **Deletion**: You can delete individual chats or clear your entire history from **Settings > Chats**.
