# Open WebUI Plugin Overview

## Extensibility

Make Open WebUI do anything with Python, HTTP, or community plugins you install in one click.

Open WebUI ships with powerful defaults, but your workflows aren't default. Extensibility is how you close the gap: give models real-time data, enforce compliance rules, add new AI providers, or connect to any external service. Write a few lines of Python, point at an OpenAPI endpoint, or browse the community library. The platform adapts to you, not the other way around.

There are three layers, and most teams end up using at least two:

- **In-process Python** (Tools & Functions) runs inside Open WebUI itself with zero infrastructure and instant iteration.
- **External HTTP** (OpenAPI & MCP servers) connects to services running anywhere, from a sidecar container to a third-party SaaS.
- **Pipeline workers** (Pipelines) offload heavy or sensitive processing to a separate container, keeping your main instance fast and clean.

## Key Features

| Feature | Description |
| :--- | :--- |
| **Tools** | Python scripts that give models new abilities: web search, API calls, code execution |
| **Functions** | Platform extensions that add model providers (Pipes), message processing (Filters), or UI actions (Actions) |
| **MCP support** | Native Streamable HTTP for Model Context Protocol servers |
| **OpenAPI servers** | Auto-discover and expose tools from any OpenAPI-compatible endpoint |
| **Pipelines** | Modular plugin framework running on a separate worker for heavy or sensitive processing |
| **Skills** | Markdown instruction sets that teach models how to approach specific tasks |
| **Prompts** | Slash-command templates with typed input variables and versioning |
| **Community library** | One-click import of community-built Tools and Functions |

## Architecture at a Glance

| Layer | Runs where | Best for | Trade-off |
|-------|-----------|----------|-----------|
| **Tools & Functions** | Inside Open WebUI process | Real-time data, filters, UI actions, new providers | Shares resources with the main server |
| **OpenAPI / MCP** | Any HTTP endpoint | Connecting existing services, third-party APIs | Requires a running external server |
| **Pipelines** | Separate Docker container | GPU workloads, heavy dependencies, sandboxed execution | Additional infrastructure to manage |

Most users start with **Tools & Functions**. They require no extra setup, have a built-in code editor, and cover the majority of use cases.

## Tools vs Functions

- **Tools** extend the abilities of LLMs, allowing them to collect real-world, real-time data like weather, stock prices, etc. Tools are like plugins that the LLM can use to gather real-world, real-time data. Tools are about model access and live in your Workspace tabs.
- **Functions** extend the capabilities of Open WebUI itself, enabling you to add new AI model support (like Anthropic or Vertex AI) or improve usability. Functions are about platform customization and are found in the Admin Panel.
- **Pipelines** are for advanced users who want to transform Open WebUI features into API-compatible workflows, mainly for offloading heavy processing.

## Security Warning

Tools, Functions, Pipes, Filters, and Pipelines execute **arbitrary Python code** on your server. This is by design.

1. **Only install from trusted sources.** Never import Tools or Functions from unknown or untrusted sources.
2. **Review code before importing.** Before installing any community Tool or Function, review its source code.
3. **Protect your data directory.** The `data` directory (mounted at `/app/backend/data` in Docker) contains your database, configurations, and cached Tools/Functions.
4. **Restrict Workspace access.** Only trusted administrators should have permission to create, import, or modify Tools and Functions.
5. **Audit installed plugins regularly.** Periodically review via **Workspace > Tools** and **Admin Panel > Functions**.

## Limitations

### Resource sharing
In-process Tools and Functions share CPU and memory with Open WebUI. Computationally expensive plugins should be moved to Pipelines or external services.

### MCP transport
Native MCP support is **Streamable HTTP only**. For stdio or SSE-based MCP servers, use [mcpo](https://github.com/open-webui/mcpo) as a translation proxy.

## Use Cases

- **Real-time data enrichment**: Tools that query CRM APIs, retrieve live deal data.
- **Enterprise compliance filters**: Filter Functions that scan for PHI patterns (SSN, MRN, dates of birth), redact before responses reach users.
- **Multi-provider model routing**: Pipe Functions to add Anthropic, Google Vertex AI, and self-hosted vLLM alongside existing Ollama models.
- **Heavy-compute pipelines**: RAG pipeline with cross-encoder re-ranking on dedicated GPU node via Pipelines.

## Dive Deeper

| Topic | What you'll learn |
|-------|-------------------|
| **Tools & Functions** | Writing Python Tools, Functions (Pipes, Filters, Actions), and the development API |
| **MCP** | Connecting Model Context Protocol servers, OAuth setup, troubleshooting |
| **Pipelines** | Deploying the pipeline worker, building custom pipelines, directory structure |
