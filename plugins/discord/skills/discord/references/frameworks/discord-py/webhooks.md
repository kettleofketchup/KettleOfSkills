---
last_updated: "2026-03-18"
description: discord.py webhooks — Webhook class, sending messages, embeds, files, editing and deleting
---

# discord.py Webhooks

Docs: https://discordpy.readthedocs.io/en/stable/

## Creating Webhooks

```python
# From a channel
webhook = await channel.create_webhook(name="My Webhook")
print(f"URL: {webhook.url}")

# From URL
webhook = discord.Webhook.from_url(
    "https://discord.com/api/webhooks/ID/TOKEN",
    session=aiohttp.ClientSession()  # or bot.http._HTTPClient session
)
```

## Sending Messages

```python
# Simple message
await webhook.send("Hello from webhook!")

# With username/avatar override
await webhook.send(
    content="Custom appearance",
    username="Custom Bot",
    avatar_url="https://example.com/avatar.png",
)

# With embed
embed = discord.Embed(title="Alert", description="Something happened", color=0xFF0000)
embed.add_field(name="Status", value="Critical", inline=True)
embed.set_footer(text="Monitoring System")
embed.timestamp = discord.utils.utcnow()

await webhook.send(embed=embed)

# Multiple embeds
await webhook.send(embeds=[embed1, embed2])  # max 10

# With file
await webhook.send(file=discord.File("report.pdf"))
await webhook.send(
    content="See attached",
    files=[discord.File("img1.png"), discord.File("img2.png")]
)

# Ephemeral (interaction webhooks only)
await webhook.send("Secret", ephemeral=True)

# Wait for message object back
msg = await webhook.send("Hello", wait=True)
print(f"Message ID: {msg.id}")
```

## Sending to Threads

```python
# Send to existing thread
await webhook.send("Thread message", thread=thread_object)

# Create thread in forum channel
await webhook.send(
    content="First post",
    thread_name="New Discussion",
)
```

## Fetching Webhooks

```python
# All webhooks in a channel
webhooks = await channel.webhooks()

# All webhooks in a guild
webhooks = await guild.webhooks()

# Specific webhook by ID
webhook = await bot.fetch_webhook(webhook_id)
```

## Editing Webhook Messages

```python
# Edit a sent message (need wait=True or message ID)
msg = await webhook.send("Original", wait=True)
await webhook.edit_message(msg.id, content="Edited content")

# Edit with new embed
new_embed = discord.Embed(title="Updated", color=0x00FF00)
await webhook.edit_message(msg.id, embed=new_embed)
```

## Deleting Webhook Messages

```python
await webhook.delete_message(msg.id)
```

## Modifying/Deleting Webhooks

```python
# Edit webhook settings
await webhook.edit(name="New Name", avatar=avatar_bytes, channel=new_channel)

# Delete webhook
await webhook.delete(reason="No longer needed")
```

## Embed Builder Pattern

```python
embed = discord.Embed(
    title="Server Status",
    description="All systems operational",
    color=discord.Color.green(),
    url="https://status.example.com",
    timestamp=discord.utils.utcnow(),
)
embed.set_author(name="StatusBot", icon_url="https://example.com/icon.png")
embed.set_thumbnail(url="https://example.com/thumb.png")
embed.set_image(url="https://example.com/banner.png")
embed.add_field(name="Uptime", value="99.9%", inline=True)
embed.add_field(name="Region", value="US-East", inline=True)
embed.add_field(name="Response Time", value="42ms", inline=True)
embed.set_footer(text="Last checked", icon_url="https://example.com/clock.png")
```

**Color shortcuts:** `discord.Color.red()`, `.green()`, `.blue()`, `.gold()`,
`.orange()`, `.purple()`, `.dark_theme()`, `.blurple()`, `.greyple()`

## Detecting Webhook Messages

```python
@bot.event
async def on_message(message):
    if message.webhook_id:
        return  # skip webhook messages
    # handle normal messages
```

## SyncWebhook (Synchronous)

For non-async contexts (e.g., Flask, Django):

```python
import discord
import requests

webhook = discord.SyncWebhook.from_url(
    "https://discord.com/api/webhooks/ID/TOKEN",
    session=requests.Session()
)
webhook.send("Sync message!")
```
