# Pipe Functions

Pipe Functions create **custom agents/models** in Open WebUI. A Pipe is essentially a custom model with specific behavior, all within the Open WebUI framework.

Pipe functions should generally be defined as `async`.

## Basic Pipe Structure

```python
from pydantic import BaseModel, Field

class Pipe:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()

    async def pipe(self, body: dict):
        print(self.valves, body)
        return "Hello, World!"
```

### The Pipe Class
- Acts as the blueprint for your plugin, determining how it behaves within Open WebUI.

### Valves: Configuring Your Pipe
- Nested class within `Pipe`, inheriting from `BaseModel`.
- Contains configuration options (parameters) that persist across use.

### The `pipe` Function
- Core function where custom logic resides.
- **Parameters**: `body` (dictionary containing input data).
- Returns the result.

## Creating Multiple Models with Pipes (Manifold)

Define a `pipes` function or variable to represent multiple models:

```python
class Pipe:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self):
        return [
            {"id": "model_id_1", "name": "model_1"},
            {"id": "model_id_2", "name": "model_2"},
            {"id": "model_id_3", "name": "model_3"},
        ]

    async def pipe(self, body: dict):
        model = body.get("model", "")
        return f"{model}: Hello, World!"
```

Each model appears individually in the Open WebUI model selector.

## OpenAI Proxy Pipe Example

```python
from pydantic import BaseModel, Field
import requests

class Pipe:
    class Valves(BaseModel):
        NAME_PREFIX: str = Field(default="OPENAI/", description="Prefix for model names.")
        OPENAI_API_BASE_URL: str = Field(default="https://api.openai.com/v1")
        OPENAI_API_KEY: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self):
        if self.valves.OPENAI_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {self.valves.OPENAI_API_KEY}", "Content-Type": "application/json"}
                r = requests.get(f"{self.valves.OPENAI_API_BASE_URL}/models", headers=headers)
                models = r.json()
                return [
                    {"id": model["id"], "name": f'{self.valves.NAME_PREFIX}{model.get("name", model["id"])}'}
                    for model in models["data"] if "gpt" in model["id"]
                ]
            except Exception as e:
                return [{"id": "error", "name": "Error fetching models."}]
        else:
            return [{"id": "error", "name": "API Key not provided."}]

    def pipe(self, body: dict, __user__: dict):
        headers = {"Authorization": f"Bearer {self.valves.OPENAI_API_KEY}", "Content-Type": "application/json"}
        model_id = body["model"][body["model"].find(".") + 1:]
        payload = {**body, "model": model_id}
        try:
            r = requests.post(
                url=f"{self.valves.OPENAI_API_BASE_URL}/chat/completions",
                json=payload, headers=headers, stream=True,
            )
            r.raise_for_status()
            if body.get("stream", False):
                return r.iter_lines()
            else:
                return r.json()
        except Exception as e:
            return f"Error: {e}"
```

## Using Internal Open WebUI Functions

```python
from pydantic import BaseModel, Field
from fastapi import Request
from open_webui.models.users import Users
from open_webui.utils.chat import generate_chat_completion

class Pipe:
    def __init__(self):
        pass

    async def pipe(self, body: dict, __user__: dict, __request__: Request) -> str:
        user = Users.get_user_by_id(__user__["id"])
        body["model"] = "llama3.2:latest"
        return await generate_chat_completion(__request__, body, user)
```

## FAQ

**Q: `pipe` vs `pipes` function?**
- `pipe`: Processes input data for a single model.
- `pipes`: Returns a list of model definitions, each appearing individually in Open WebUI.

**Q: Can I create a Pipe without Valves?**
Yes, but including Valves is good practice for flexibility.

**Q: How to handle API keys securely?**
Never hard-code. Use Valves to input and store API keys securely.

**Q: Can I use external libraries?**
Yes, import and use as needed. Ensure dependencies are installed.

**Q: Best practices for organizing Pipe code?**
- Keep `Valves` at top of `Pipe` class
- Initialize variables in `__init__`, primarily `self.valves`
- Place `pipe` function after `__init__`
- Use clear, descriptive variable names
