---
last_updated: "2026-03-18"
description: discord.py UI components — Views, Buttons, Select Menus, Modals, TextInput, interaction callbacks
---

# discord.py Components

Docs: https://discordpy.readthedocs.io/en/stable/

## Views (discord.ui.View)

Container for interactive components. Subclass to add buttons/selects.

```python
import discord
from discord import ui

class MyView(ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # 180s timeout, None = no timeout

    @ui.button(label="Click me", style=discord.ButtonStyle.primary)
    async def my_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Clicked!", ephemeral=True)

    @ui.select(placeholder="Choose...", options=[
        discord.SelectOption(label="A", value="a"),
        discord.SelectOption(label="B", value="b"),
    ])
    async def my_select(self, interaction: discord.Interaction, select: ui.Select):
        await interaction.response.send_message(f"Selected: {select.values[0]}")

# Send view
await interaction.response.send_message("Hello", view=MyView())
```

**Persistent views** survive bot restarts — register with `bot.add_view(MyView())`.
Require `custom_id` on all components and `timeout=None`.

## Buttons (discord.ui.Button)

```python
@ui.button(label="Confirm", style=discord.ButtonStyle.success, custom_id="confirm")
async def confirm(self, interaction: discord.Interaction, button: ui.Button):
    button.disabled = True
    await interaction.response.edit_message(view=self)
```

**ButtonStyle enum:**
- `primary` (blurple) | `secondary` (grey) | `success` (green)
- `danger` (red) | `link` (grey, opens URL — no callback)

Link buttons: `ui.Button(label="Docs", url="https://...")`

## Select Menus

**String Select (discord.ui.Select):**
```python
@ui.select(placeholder="Pick a color", min_values=1, max_values=2, options=[
    discord.SelectOption(label="Red", value="red", emoji="🔴"),
    discord.SelectOption(label="Blue", value="blue", description="Ocean color"),
])
async def color_select(self, interaction, select):
    await interaction.response.send_message(f"Picked: {', '.join(select.values)}")
```

**Auto-populated selects:**
```python
@ui.select(cls=ui.UserSelect, placeholder="Pick a user", min_values=1, max_values=5)
async def user_select(self, interaction, select):
    users = select.values  # list of discord.Member/User
    await interaction.response.send_message(f"Selected {len(users)} users")
```

Available classes: `ui.UserSelect`, `ui.RoleSelect`, `ui.ChannelSelect`, `ui.MentionableSelect`

ChannelSelect supports `channel_types` parameter to filter.

## Modals (discord.ui.Modal)

```python
class FeedbackModal(ui.Modal, title="Feedback Form"):
    name = ui.TextInput(label="Name", placeholder="Your name", max_length=100)
    feedback = ui.TextInput(
        label="Feedback",
        style=discord.TextStyle.paragraph,
        placeholder="Enter feedback...",
        min_length=10,
        max_length=1000,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks {self.name.value}!\n{self.feedback.value}", ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message("Something went wrong", ephemeral=True)
```

**Trigger modal from button/command:**
```python
await interaction.response.send_modal(FeedbackModal())
```

**TextStyle enum:** `short` (single-line), `paragraph` (multi-line)

## Interaction Response Methods

| Method | Use |
|--------|-----|
| `interaction.response.send_message(content, ephemeral=True)` | Reply with message |
| `interaction.response.defer(ephemeral=True)` | Ack, show "thinking..." |
| `interaction.response.edit_message(content, view)` | Edit originating message |
| `interaction.response.send_modal(modal)` | Show modal form |
| `interaction.response.autocomplete(choices)` | Return autocomplete |
| `interaction.followup.send(content)` | Send followup after response |
| `interaction.edit_original_response(content)` | Edit after defer |
| `interaction.delete_original_response()` | Delete response |

Only one `response.*` call per interaction. Use `followup` for additional messages.

## Disabling Components

```python
for child in self.children:
    child.disabled = True
await interaction.response.edit_message(view=self)
```

## View Timeout

```python
class MyView(ui.View):
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
```
