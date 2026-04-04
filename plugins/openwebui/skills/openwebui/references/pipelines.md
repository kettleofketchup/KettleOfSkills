# Pipelines

Pipelines bring modular, customizable workflows to any UI client supporting OpenAI API specs. Use Pipelines when dealing with computationally heavy tasks you want to offload from the main Open WebUI instance.

**Do NOT use Pipelines** if your goal is simply adding support for additional providers like Anthropic or basic filters -- use Open WebUI Functions instead.

## Quick Start with Docker

1. Run the container:
```sh
docker run -d -p 9099:9099 --add-host=host.docker.internal:host-gateway -v pipelines:/app/pipelines --name pipelines --restart always ghcr.io/open-webui/pipelines:main
```

2. Connect to Open WebUI:
   - Admin Panel > Settings > Connections > + button
   - API URL: `http://localhost:9099` (or `host.docker.internal` if Open WebUI is in Docker)
   - API key: `0p3n-w3bu!`

3. Manage Configurations:
   - Admin Panel > Settings > Pipelines tab
   - Select pipeline, modify valve values

### Custom Pipeline with Dependencies

```sh
docker run -d -p 9099:9099 --add-host=host.docker.internal:host-gateway \
  -e PIPELINES_URLS="https://github.com/open-webui/pipelines/blob/main/examples/filters/detoxify_filter_pipeline.py" \
  -v pipelines:/app/pipelines --name pipelines --restart always ghcr.io/open-webui/pipelines:main
```

## Installation from Source

1. Python 3.11 required (only supported version)
2. Clone and install:
```sh
git clone https://github.com/open-webui/pipelines.git
cd pipelines
pip install -r requirements.txt
sh ./start.sh
```

## Directory Structure

The `/pipelines` directory is the core. All pipelines are **automatically loaded** when the server launches. Change directory with `PIPELINES_DIR` env variable.

## Examples

- **Function Calling Pipeline**: Handle function calls with custom logic
- **Custom RAG Pipeline**: Retrieval-Augmented Generation with LlamaIndex
- **Message Monitoring (Langfuse)**: Monitor interactions in real-time
- **Rate Limit Filter**: Control request flow
- **Real-Time Translation (LibreTranslate)**: Seamless translations
- **Toxic Message Filter**: Detect and handle toxic messages

## Filters (Pipeline Type)

Filters perform actions against incoming user messages and outgoing assistant messages. Use cases: monitoring (Langfuse, DataDog), content modification, blocking toxic messages, translation, rate limiting.

When a filter pipeline is enabled on a model or pipe:
1. Incoming user message ("inlet") passes to filter
2. Filter processes and modifies the message
3. Chat completion is requested from LLM
4. Filter post-processes outgoing LLM message ("outlet")
5. Processed response sent to user

## Pipes (Pipeline Type)

Pipes are standalone functions that process inputs and generate responses, possibly invoking LLMs or external services. Use cases: RAG, non-OpenAI LLM providers (Anthropic, Azure, Google), function execution.

Pipes show up as a new model with an "External" designation in the WebUI.

## Valves in Pipelines

`Valves` are input variables set per pipeline. Set as subclass of `Pipeline` class, initialized in `__init__`.

Use `os.getenv()` with defaults for admin reconfigurability:

```python
self.valves = self.Valves(
    **{
        "LLAMAINDEX_OLLAMA_BASE_URL": os.getenv("LLAMAINDEX_OLLAMA_BASE_URL", "http://localhost:11434"),
        "LLAMAINDEX_MODEL_NAME": os.getenv("LLAMAINDEX_MODEL_NAME", "llama3"),
    }
)
```

Or use `Optional` type to allow loading without a value:

```python
class Pipeline:
    class Valves(BaseModel):
        target_user_roles: List[str] = ["user"]
        max_turns: Optional[int] = None
```

If you don't provide a way for valves to be updated in the web UI, you'll get:
`WARNING:root:No Pipeline class found in <pipeline name>`

## Tutorials

- [Monitoring Open WebUI with Filters](https://medium.com/@0xthresh/monitor-open-webui-with-datadog-llm-observability-620ef3a598c6) - DataDog LLM observability
- [Building Customized Text-To-SQL Pipelines](https://www.youtube.com/watch?v=y7frgUWrcT4)
- [Demo and Code Review for Text-To-SQL](https://www.youtube.com/watch?v=iLVyEgxGbg4)
- [Deploying custom Document RAG pipeline](https://github.com/Sebulba46/document-RAG-pipeline)
