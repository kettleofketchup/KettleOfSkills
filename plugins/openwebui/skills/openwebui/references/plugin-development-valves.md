# Valves and UserValves

Valves and UserValves allow users to provide dynamic details such as API keys or configuration options. They create fillable fields or bool switches in the GUI menu. Always optional but highly encouraged.

Valves and UserValves can be defined in `Pipe`, `Pipeline`, `Filter` or `Tools` classes.

- **Valves**: Configurable by admins only via Tools or Functions menus.
- **UserValves**: Configurable by any user from a chat session.

## Example

```python
from pydantic import BaseModel, Field
from typing import Literal

class Filter:
    class Valves(BaseModel):
        test_valve: int = Field(
            default=4,
            description="A valve controlling a numerical value"
        )
        choice_option: Literal["choiceA", "choiceB"] = Field(
            default="choiceA",
            description="An example of a multi choice valve",
        )
        priority: int = Field(
            default=0,
            description="Priority level for filter operations. Lower values are passed through first"
        )
        pass

    class UserValves(BaseModel):
        test_user_valve: bool = Field(
            default=False, description="A user valve controlling a True/False switch"
        )
        pass

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict, __user__: dict):
        # UserValves are available via __user__["valves"]
        test_user_valve = __user__["valves"].test_user_valve
        # Or: test_user_valve = dict(__user__["valves"])["test_user_valve"]
        # Do NOT use: __user__["valves"]["test_user_valve"]  # Returns default, not actual value
```

## Input Types

### Password Input (Masked Fields)

```python
class Tools:
    class UserValves(BaseModel):
        service_password: str = Field(
            default="",
            description="Your service password",
            json_schema_extra={"input": {"type": "password"}}
        )
```

Renders as masked input with toggle to reveal value.

### Select Dropdown Input

#### Static Options

```python
class Tools:
    class Valves(BaseModel):
        priority: str = Field(
            default="medium",
            description="Processing priority level",
            json_schema_extra={"input": {"type": "select", "options": ["low", "medium", "high"]}}
        )
```

Label/value pairs:

```python
json_schema_extra={
    "input": {
        "type": "select",
        "options": [
            {"value": "debug", "label": "Debug (Verbose)"},
            {"value": "info", "label": "Info (Standard)"},
            {"value": "warn", "label": "Warning (Minimal)"},
            {"value": "error", "label": "Error (Critical Only)"}
        ]
    }
}
```

#### Dynamic Options

Specify a method name as a string. Called when config UI is rendered:

```python
class Tools:
    class Valves(BaseModel):
        selected_model: str = Field(
            default="",
            description="Choose a model",
            json_schema_extra={"input": {"type": "select", "options": "get_model_options"}}
        )

        @classmethod
        def get_model_options(cls, __user__=None) -> list[dict]:
            return [
                {"value": "gpt-4", "label": "GPT-4"},
                {"value": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo"},
            ]
```

Dynamic options support an optional `__user__` parameter for user-specific options:

```python
class Tools:
    class UserValves(BaseModel):
        workspace: str = Field(
            default="",
            description="Select your workspace",
            json_schema_extra={"input": {"type": "select", "options": "get_user_workspaces"}}
        )

        @classmethod
        def get_user_workspaces(cls, __user__=None) -> list[dict]:
            if not __user__:
                return []
            return [
                {"value": "ws-1", "label": "Personal Workspace"},
                {"value": "ws-2", "label": "Team Workspace"}
            ]
```

Dynamic options are useful for: fetching available API models, loading database options, presenting user-specific resources, options that change based on runtime context.
