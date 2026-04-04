# FAQ

### Q: How can I get support or ask for help?

**A:** Community support for Open WebUI is provided by **volunteers**. Responses are best-effort. For dedicated, guaranteed support, check out the **Enterprise offerings**.

**To get the best help:**
1. **Search first.** Check docs, Discord, Reddit, GitHub Discussions, and Issues.
2. **Try the Discord bot.** In the **#questions** channel, ping the bot with your question.
3. **Provide details.** Include: Open WebUI version, deployment method (Docker/pip), model provider and model name, relevant settings, and steps to reproduce.
4. **Be kind.** Contributors volunteer their limited time.

**Where to ask:**
- Quick Answers: Discord #questions channel (try the bot first)
- Bugs: GitHub Issues (use the issue template)
- Questions & Help: Discord, Reddit, or GitHub Discussions
- Feature Requests: GitHub Discussions

### Q: How do I customize the logo and branding?

**A:** You can customize the theme, logo, and branding with an **Enterprise License**, which unlocks exclusive enterprise features.

### Q: Is my data being sent anywhere?

**A:** No, your data is never sent anywhere unless you explicitly choose to share it or connect an external model provider. Everything runs and is stored locally on your machine or server. The entire codebase is hosted publicly for inspection.

### Q: How can I see a list of all the chats I've ever shared?

**A:** Open WebUI provides a centralized **Shared Chats** dashboard via **Settings > Data Controls > Shared Chats > Manage**. From there you can search, re-copy links, or revoke access.

### Q: How can I manage or delete files I've uploaded?

**A:** Access the **File Manager** at **Settings > Data Controls > Manage Files > Manage**. Deleting a file also cleans up associated Knowledge Base entries and vector embeddings.

### Q: Can I use Open WebUI offline, in air-gapped networks, or in extreme environments?

**A:** **Yes.** Open WebUI is a fully self-hosted, **internet-independent AI platform**. It runs entirely on local hardware with zero external calls. It works in air-gapped networks, submarines, polar research stations, underground facilities, disaster zones, and any environment where cloud-based systems are impractical.

### Q: Why am I asked to sign up? Where are my data being sent to?

**A:** Signup is required to create the admin user for security. If Open WebUI is ever exposed externally, your data remains secure. Everything is kept local; we do not collect your data.

### Q: Why can't my Docker container connect to services on the host using `localhost`?

**A:** Inside a Docker container, `localhost` refers to the container itself. Use `host.docker.internal` instead to connect to host services.

### Q: How do I make my host's services accessible to Docker containers?

**A:** Configure services to listen on `0.0.0.0` instead of `127.0.0.1`. Implement appropriate security measures (firewalls, authentication).

### Q: Why isn't my Open WebUI updating?

**A:** You must pull the latest image, then stop and remove the existing container, then start a new one:

```bash
docker pull ghcr.io/open-webui/open-webui:main
docker stop open-webui
docker rm open-webui
docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

### Q: Won't I lose my data if I delete my container?

**A:** Your data is safe **only if you have a Volume configured**. If you ran your container *without* the `-v open-webui:/app/backend/data` flag, your data is stored **inside** the container and deleting it **will result in permanent data loss**.

When you use a Volume, your data stays safe even when the container is deleted.

**Default Data Path:** `/var/lib/docker/volumes/open-webui/_data`

### Q: Should I use the distro-packaged Docker or the official Docker package?

**A:** Use the official Docker package. It's frequently updated with latest features, bug fixes, and security patches, and supports `host.docker.internal`.

### Q: Is GPU support available in Docker?

**A:** GPU support is available in Docker for Windows and Docker Engine on Linux. Docker Desktop for Linux and macOS do not currently offer GPU support.
