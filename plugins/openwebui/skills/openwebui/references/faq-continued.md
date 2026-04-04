# FAQ (Continued)

### Q: Why does Open WebUI emphasize the use of Docker?

**A:** Docker ensures consistency, isolates dependencies, and simplifies deployment across environments. It minimizes compatibility issues regardless of the underlying system. While Docker has a learning curve, the advantages for deployment and maintenance are significant.

### Q: Why doesn't Speech-to-Text (STT) and Text-to-Speech (TTS) work in my deployment?

**A:** STT and TTS services may require HTTPS. Modern browsers restrict these features to secure HTTPS connections. Ensure your deployment is accessible over HTTPS.

### Q: Why doesn't Open WebUI include built-in HTTPS support?

**A:** Implementing HTTPS directly could limit flexibility. HTTPS termination is left to users for production deployments, allowing greater adaptability and customization.

### Q: I updated/restarted/installed some new software and now Open WebUI isn't working!

**A:** This is likely related to a direct installation (non-Docker) without a virtual environment. Direct installations are sensitive to system changes. Use a virtual environment for managing backend dependencies.

### Q: I updated/restarted and now I'm being logged out, or getting "Error decrypting tokens" for my tools?

**A:** You haven't set a persistent `WEBUI_SECRET_KEY`. Without it, Open WebUI generates a random one on each start, invalidating session cookies and preventing decryption of stored secrets.

**Fix:** Set `WEBUI_SECRET_KEY` to a constant, secure string in your Docker Compose or environment config.

### Q: I updated/restarted and now my login isn't working, I had to create a new account and all my chats are gone.

**A:** This happens when a Docker container is created without mounting a volume for `/app/backend/data` or if the volume was unintentionally deleted. Ensure your Docker run command includes a volume mount.

### Q: I tried to login and couldn't, made a new account and now I'm told my account needs admin activation.

**A:** The first account created is automatically the admin. Creating a new account without admin access requires admin activation. See the Resetting the Admin Password guide.

### Q: Why can't Open WebUI start with an SSL error?

**A:** Likely due to absent SSL certificates or incorrect HuggingFace configuration. Set up a mirror:

```bash
docker run -d -p 3000:8080 -e HF_ENDPOINT=https://hf-mirror.com/ --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

### Q: Why are my reasoning model's thinking blocks showing as raw text?

**A:** The model's thinking tags are not recognized by Open WebUI. Customize the tags in the model's Advanced Parameters.

### Q: RAG with Open WebUI is very bad or not working. Why?

**A:** If using **Ollama**, the default context length is **2048 tokens**, which may be too small for retrieved data. **Increase the context length to 8192+ tokens** in your Ollama model params (chat settings or model editor page).

### Q: I'm getting "The content provided is empty" when uploading files via the API.

**A:** This is a **race condition**. The upload endpoint returns immediately, but extraction and embedding happen asynchronously. Poll the file status endpoint until processing is complete:

```python
import requests
import time

def wait_for_processing(token, file_id):
    url = f'http://localhost:3000/api/v1/files/{file_id}/process/status'
    headers = {'Authorization': f'Bearer {token}'}
    while True:
        status = requests.get(url, headers=headers).json().get('status')
        if status == 'completed':
            return True
        elif status == 'failed':
            raise Exception("Processing failed")
        time.sleep(2)
```

### Q: I asked the model what it is and it gave the wrong answer. Is Open WebUI routing to the wrong model?

**A:** No. **LLMs do not reliably know their own identity.** Models frequently claim to be a different model, give outdated info, or hallucinate version numbers. To verify your model, check the model selector in the UI or Admin Panel > Settings > Connections.

### Q: Why can models on official interfaces (ChatGPT, Claude.ai) correctly identify themselves?

**A:** The provider **injects a system prompt** that tells the model what it is. You can do the same in Open WebUI by adding a system prompt to your model configuration.

### Q: Why am I seeing multiple API requests when I only send one message?

**A:** Open WebUI uses **Task Models** for background features: title generation, tag generation, query generation for RAG, web search queries, and autocomplete suggestions.

**To reduce API costs:**
1. Go to **Admin Panel > Settings > Interface** for title/tag generation settings.
2. Configure a **Task Model** under **Admin Panel > Settings > Models** to use a smaller, cheaper model.
3. Disable features you don't need.

Set your Task Model to a fast, inexpensive model (or a local model via Ollama) while keeping your primary chat model as the capable one.

### Q: Is MCP (Model Context Protocol) supported?

**A:** Yes. Open WebUI includes **native support for MCP Streamable HTTP**. For other MCP transports, use the official proxy adapter **MCPO** at `github.com/open-webui/mcpo`.

### Q: Why doesn't Open WebUI natively support [Provider X]'s proprietary API?

**A:** Open WebUI's core supports **universal protocols** (OpenAI Chat Completions). Provider-specific APIs are handled through the **pipes** plugin system. Community-maintained provider integrations are available for one-click install. Middleware proxies (LiteLLM, OpenRouter) can also translate proprietary APIs.

Experimental support: Connections can optionally be configured to use **Open Responses** (`openresponses.org`), an open specification for multi-provider interoperability.

### Q: Is Open WebUI scalable for large organizations?

**A:** Yes. Open WebUI supports tens to hundreds of thousands of seats. Its stateless, container-first architecture supports horizontal scaling, flexible storage backends, externalized authentication and database support, and full container orchestration compatibility (Kubernetes, Docker Swarm).

### Q: How often is Open WebUI updated?

**A:** Major releases are aimed weekly, with bug fixes as needed. Follow the GitHub Releases page.

### Q: Where do I report non-compliant deployments that violate the license?

**A:** Email **reports@openwebui.com** with relevant details (screenshots, URLs, description).
