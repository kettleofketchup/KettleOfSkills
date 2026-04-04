---
last_updated: "2026-03-18"
description: discord.py application commands — app_commands, hybrid commands, tree sync, groups, options, error handling
---

# discord.py Slash Commands

Docs: https://discordpy.readthedocs.io/en/stable/

## Bot Setup

```python
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # required for prefix commands
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # sync global commands
    # await bot.tree.sync(guild=discord.Object(id=GUILD_ID))  # guild-specific
    print(f"Synced commands for {bot.user}")
```

## Basic Slash Command

```python
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")
```

## Command with Options

```python
@bot.tree.command(name="ban", description="Ban a member")
@app_commands.describe(member="The member to ban", reason="Reason for ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Banned {member.mention}: {reason}")
```

**Supported parameter types** (auto-converted from Discord option types):
`str`, `int`, `float`, `bool`, `discord.Member`, `discord.User`, `discord.Role`,
`discord.TextChannel`, `discord.VoiceChannel`, `discord.CategoryChannel`,
`discord.Attachment`, `app_commands.Range[int, min, max]`, `app_commands.Range[float, min, max]`

## Choices

```python
@bot.tree.command(name="color")
@app_commands.choices(color=[
    app_commands.Choice(name="Red", value="red"),
    app_commands.Choice(name="Blue", value="blue"),
    app_commands.Choice(name="Green", value="green"),
])
async def color(interaction: discord.Interaction, color: app_commands.Choice[str]):
    await interaction.response.send_message(f"You picked {color.name} ({color.value})")
```

## Autocomplete

```python
async def fruit_autocomplete(interaction: discord.Interaction, current: str):
    fruits = ["Apple", "Banana", "Cherry", "Dragonfruit"]
    return [
        app_commands.Choice(name=f, value=f)
        for f in fruits if current.lower() in f.lower()
    ][:25]

@bot.tree.command(name="fruit")
@app_commands.autocomplete(fruit=fruit_autocomplete)
async def fruit(interaction: discord.Interaction, fruit: str):
    await interaction.response.send_message(f"You chose {fruit}")
```

## Command Groups

```python
group = app_commands.Group(name="settings", description="Manage settings")

@group.command(name="get", description="Get a setting")
async def settings_get(interaction: discord.Interaction, key: str):
    await interaction.response.send_message(f"Setting {key}: ...")

@group.command(name="set", description="Set a setting")
async def settings_set(interaction: discord.Interaction, key: str, value: str):
    await interaction.response.send_message(f"Set {key} = {value}")

bot.tree.add_command(group)
```

## Hybrid Commands

Work as both prefix (`!cmd`) and slash (`/cmd`):

```python
@bot.hybrid_command(name="info", description="Get user info")
async def info(ctx: commands.Context, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"{member.name} joined {member.joined_at}")
```

Sync required: `await bot.tree.sync()`

## Context Menu Commands

```python
@bot.tree.context_menu(name="Get User Info")
async def user_info(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"{user.name}: {user.id}", ephemeral=True)

@bot.tree.context_menu(name="Bookmark Message")
async def bookmark(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(f"Bookmarked: {message.jump_url}", ephemeral=True)
```

## Error Handling

```python
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You lack permissions", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Cooldown: {error.retry_after:.1f}s", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred", ephemeral=True)
        raise error
```

**Per-command error handler:**
```python
@my_command.error
async def my_command_error(interaction: discord.Interaction, error):
    ...
```

## Checks & Cooldowns

```python
@bot.tree.command()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
async def admin_cmd(interaction: discord.Interaction):
    ...
```

## Syncing Commands

```python
# Global (up to 1h propagation)
await bot.tree.sync()

# Guild-specific (instant)
await bot.tree.sync(guild=discord.Object(id=123456))

# Copy global to guild for testing
bot.tree.copy_global_to(guild=discord.Object(id=123456))
await bot.tree.sync(guild=discord.Object(id=123456))

# Clear guild commands
bot.tree.clear_commands(guild=discord.Object(id=123456))
await bot.tree.sync(guild=discord.Object(id=123456))
```
