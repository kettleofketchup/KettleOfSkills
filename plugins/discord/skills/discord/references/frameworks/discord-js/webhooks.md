---
last_updated: "2026-03-18"
description: discord.js webhooks and embeds — WebhookClient, EmbedBuilder, sending/editing/deleting webhook messages
---

# discord.js Webhooks & Embeds

Docs: https://discord.js.org | Guide: https://discordjs.guide

## WebhookClient

Sends messages without a bot client connection.

```javascript
const { WebhookClient, EmbedBuilder } = require('discord.js');

// From ID + token
const webhook = new WebhookClient({ id: 'WEBHOOK_ID', token: 'WEBHOOK_TOKEN' });

// From URL
const webhook = new WebhookClient({ url: 'https://discord.com/api/webhooks/ID/TOKEN' });
```

## Sending Messages

```javascript
// Simple text
await webhook.send('Hello from webhook!');

// With overrides
await webhook.send({
  content: 'Custom message',
  username: 'Alert Bot',
  avatarURL: 'https://example.com/avatar.png',
});

// With embed
const embed = new EmbedBuilder()
  .setTitle('Status Update')
  .setDescription('All systems operational')
  .setColor(0x00FF00);

await webhook.send({ embeds: [embed] });

// With files
const { AttachmentBuilder } = require('discord.js');
const file = new AttachmentBuilder('./report.pdf');
await webhook.send({ files: [file] });
```

## Creating Webhooks (from channel)

```javascript
const webhook = await channel.createWebhook({
  name: 'My Webhook',
  avatar: 'https://example.com/avatar.png',
});
console.log(`Created: ${webhook.url}`);
```

## Fetching Webhooks

```javascript
// Channel webhooks
const channelHooks = await channel.fetchWebhooks();

// Guild webhooks
const guildHooks = await guild.fetchWebhooks();

// Single webhook
const hook = await client.fetchWebhook('WEBHOOK_ID');
```

## Message Operations

```javascript
// Fetch a message
const msg = await webhook.fetchMessage('MESSAGE_ID');

// Edit a message
await webhook.editMessage('MESSAGE_ID', {
  content: 'Updated content',
  embeds: [new EmbedBuilder().setTitle('Revised')],
});

// Delete a message
await webhook.deleteMessage('MESSAGE_ID');
```

## Editing/Deleting Webhooks

```javascript
await webhook.edit({
  name: 'New Name',
  avatar: 'https://example.com/new-avatar.png',
  channel: 'CHANNEL_ID',
});

await webhook.delete('No longer needed');
```

## Detecting Webhook Messages

```javascript
client.on(Events.MessageCreate, (message) => {
  if (message.webhookId) return;  // skip webhook messages
  // handle regular messages
});

// Get webhook that sent a message
const sourceWebhook = await message.fetchWebhook();
```

## Thread Support

```javascript
// Send to existing thread
await webhook.send({ content: 'Thread message', threadId: 'THREAD_ID' });
```

---

## EmbedBuilder

### Full Builder Pattern

```javascript
const { EmbedBuilder } = require('discord.js');

const embed = new EmbedBuilder()
  .setColor(0x0099FF)
  .setTitle('Embed Title')
  .setURL('https://discord.js.org/')
  .setAuthor({
    name: 'Author Name',
    iconURL: 'https://example.com/icon.png',
    url: 'https://example.com',
  })
  .setDescription('Main content of the embed')
  .setThumbnail('https://example.com/thumb.png')
  .addFields(
    { name: 'Field 1', value: 'Value 1', inline: true },
    { name: 'Field 2', value: 'Value 2', inline: true },
    { name: '\u200B', value: '\u200B' },  // blank separator
    { name: 'Full Width', value: 'Takes entire row' },
  )
  .setImage('https://example.com/banner.png')
  .setTimestamp()
  .setFooter({ text: 'Footer text', iconURL: 'https://example.com/footer.png' });
```

### Plain Object Alternative

```javascript
const embed = {
  color: 0x0099FF,
  title: 'Title',
  url: 'https://discord.js.org',
  author: { name: 'Author', icon_url: 'https://example.com/icon.png' },
  description: 'Description text',
  fields: [
    { name: 'Field', value: 'Value', inline: true },
  ],
  image: { url: 'https://example.com/image.png' },
  timestamp: new Date().toISOString(),
  footer: { text: 'Footer', icon_url: 'https://example.com/footer.png' },
};
```

### Attaching Local Images

```javascript
const { AttachmentBuilder } = require('discord.js');

const file = new AttachmentBuilder('./images/chart.png');
const embed = new EmbedBuilder()
  .setTitle('Weekly Report')
  .setImage('attachment://chart.png');  // reference by filename

await channel.send({ embeds: [embed], files: [file] });
```

### Editing Existing Embeds

```javascript
// Clone + modify received embed
const received = message.embeds[0];
const updated = EmbedBuilder.from(received).setTitle('Updated Title');
await message.edit({ embeds: [updated] });
```

### Limits

| Constraint | Max |
|-----------|-----|
| Title | 256 chars |
| Description | 4096 chars |
| Fields | 25 per embed |
| Field name | 256 chars |
| Field value | 1024 chars |
| Footer text | 2048 chars |
| Author name | 256 chars |
| Embeds per message | 10 |
| Total chars across all embeds | 6000 |
