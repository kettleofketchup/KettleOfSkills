# Data Controls

The **Data Controls** section in Open WebUI provides tools for managing your personal data, including files, shared content, and chat history. Access it via **Settings > Data Controls**.

## Resources

- File Management - Centralized management for all your uploaded documents
- Shared Chats - Manage and revoke access to your shared chat links
- Archived Chats - Restore or permanently delete archived conversations
- Import & Export - Backup and restore your chat history

---

# Shared Chats Management

Open WebUI provides a centralized dashboard to manage every chat conversation you have shared. This feature allows users to audit their shared content and quickly revoke access if needed.

This page documents the **management dashboard** for shared chats. For information on how to share chats, see the Chat Sharing documentation.

## Accessing the Management Dashboard

1. Click on your **profile name** or avatar in the bottom-left corner of the sidebar.
2. Select **Settings** from the menu.
3. Navigate to the **Data Controls** tab.
4. Locate the **Shared Chats** row and click the **Manage** button.

## Dashboard Features

The **Shared Chats** modal provides a unified interface for your public content:

- **Centralized List**: View all conversations that have an active share link.
- **Search & Filter**: Quickly find specific shared chats by title. The search bar includes a **500ms debounce** to ensure smooth performance while typing.
- **Advanced Sorting**: Organize your shared history by:
  - **Updated At** (Default)
  - **Title**
- **Copy Link**: Use the **Clipboard icon** next to any entry to instantly copy the share URL back to your clipboard.
- **Revoke Access (Unshare)**: Use the **Unshare icon** (represented by a slashed link) to deactivate a share link. Revoking access immediately invalidates the link. Anyone attempting to visit the URL will receive a "Not Found" error. This action is permanent, though you can generate a *new* unique link by sharing the chat again from the main interface.
- **Pagination**: Efficiently browse through your history using the "Load More" functionality at the bottom of the list.

## FAQ

**Q: Does unsharing a chat delete the original conversation?**
**A:** No. Unsharing only deletes the public link. Your original chat history remains completely intact.

**Q: Can I manage chats I've shared on the community platform here?**
**A:** No. This dashboard manages links generated on your local instance. For community-shared content, see the Deleting Shared Chats section.

**Q: If I delete my original chat, what happens to the shared link?**
**A:** Deleting a chat also immediately invalidates and deletes any associated share links.

---

# Archived Chats

Open WebUI allows you to archive conversations to declutter your sidebar while preserving them for future reference. The **Archived Chats** dashboard lets you manage all your archived conversations in one place.

## Accessing Archived Chats

1. Click on your **profile name** or avatar in the bottom-left corner of the sidebar.
2. Select **Settings** from the menu.
3. Navigate to the **Data Controls** tab.
4. Locate the **Archived Chats** row and click the **Manage** button.

## Dashboard Features

The **Archived Chats** modal provides tools to manage your archived conversations:

- **Search**: Quickly find archived chats by title using the search bar.
- **Restore**: Bring an archived chat back to your main sidebar.
- **Delete**: Permanently remove an archived chat from your account.

## Bulk Operations

From the Data Controls tab, you can also perform bulk operations:

- **Archive All Chats**: Move all your current conversations to the archive at once. This is useful for periodic cleanup.
- **Delete All Chats**: Permanently remove all conversations (both active and archived). This action cannot be undone. All chat history will be permanently deleted.

## FAQ

**Q: Can I search within archived chats?**
**A:** The archive dashboard searches by chat title. To search within message content, you would need to restore the chat first.

**Q: Is there a limit to how many chats I can archive?**
**A:** There is no hard limit. The scalability depends on your database configuration.

**Q: Do archived chats still use storage?**
**A:** Yes. Archived chats remain in your database. To free up space, you must permanently delete them.

---

# File Management

Open WebUI provides a comprehensive file management system that allows you to upload, organize, and utilize your documents across various features like Knowledge Bases and RAG.

## Centralized File Manager

The **Centralized File Manager** provides a unified interface to view, search, and manage every file you have uploaded to your Open WebUI instance, whether it was uploaded directly to a chat or into a Knowledge Base.

### Accessing the File Manager

1. Click on your **profile name** or avatar in the bottom-left corner.
2. Select **Settings** from the menu.
3. Navigate to the **Data Controls** tab.
4. Locate the **Manage Files** row and click the **Manage** button.

### Key Features

- **Universal Search**: Quickly find any file by its filename using the integrated search bar.
- **Advanced Sorting**: Organize your file list by:
  - **Filename**: Sort alphabetically to find specific documents.
  - **Created At**: See your most recent uploads or find older files.
- **File Details**: View important information at a glance, including:
  - **File Size**: See how much space each document occupies (e.g., KB, MB).
  - **Upload Date**: Track when each file was added to your instance.
- **Built-in Viewer**: Click on any file to open the **File Item Viewer**, which displays the file's metadata and specific details (such as size and type).
- **Safe Deletion**: Easily remove files you no longer need. When you delete a file through the File Manager, Open WebUI automatically performs a deep cleanup. It removes the file from all associated Knowledge Bases and deletes its corresponding vector embeddings, ensuring your database stays clean and efficient.

## Using Files in Open WebUI

### 1. Retrieval Augmented Generation (RAG)
By uploading documents (PDFs, Word docs, text files, etc.), you can ground your AI's responses in your own data.
- **Chat Uploads**: Simply drag and drop files into a chat or use the upload icon.
- **Knowledge Bases**: Add files to structured collections for more permanent and organized retrieval.

### 2. File Metadata
Every file carries metadata that helps both you and the AI understand its context. This includes content type, original filename, and size.

## Best Practices

- **Naming Conventions**: Use clear, descriptive filenames. This improves the accuracy of the File Manager's search and helps you identify specific documents.
- **Regular Audits**: Periodically use the **Manage Files** dashboard to delete old or redundant documents. This saves disk/database space and improves the performance of your system by ensuring only relevant data is retained.

## FAQ

**Q: If I delete a file, is it gone from my chats?**
**A:** Yes. Deleting a file via the File Manager removes it from the system entirely. Any chat that referenced that file using RAG will no longer be able to pull information from it.

**Q: Can I download my files back from the File Manager?**
**A:** Currently, the File Manager focuses on viewing metadata and management (deletion). To download a file, you should typically access it from the original chat or Knowledge Base where it was used.

**Q: Are there limits on the number of files I can manage?**
**A:** There is no hard-coded limit in Open WebUI. The scalability depends on your storage (disk/S3) and your Vector Database (e.g., ChromaDB, PGVector).

**Q: Does managing files require Admin privileges?**
**A:** Regular users can manage their *own* uploaded files. Administrators have additional tools to manage global files and configuration via the Admin Panel.
