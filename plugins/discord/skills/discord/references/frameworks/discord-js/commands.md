---
last_updated: "2026-03-18"
description: discord.js slash commands — SlashCommandBuilder, response methods, options, subcommands, registering, permissions
---

# discord.js Slash Commands

Docs: https://discord.js.org | Guide: https://discordjs.guide

## Bot Setup

```javascript
const { Client, Events, GatewayIntentBits } = require('discord.js');

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  if (interaction.commandName === 'ping') {
    await interaction.reply('Pong!');
  }
});

client.login(process.env.DISCORD_TOKEN);
```

## Defining Commands (SlashCommandBuilder)

```javascript
const { SlashCommandBuilder } = require('discord.js');

const ping = new SlashCommandBuilder()
  .setName('ping')
  .setDescription('Check bot latency');

const ban = new SlashCommandBuilder()
  .setName('ban')
  .setDescription('Ban a member')
  .addUserOption(opt => opt.setName('target').setDescription('User to ban').setRequired(true))
  .addStringOption(opt => opt.setName('reason').setDescription('Ban reason').setMaxLength(200))
  .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers);
```

## Option Types

```javascript
builder
  .addStringOption(opt => opt.setName('text').setDescription('...'))
  .addIntegerOption(opt => opt.setName('count').setDescription('...').setMinValue(1).setMaxValue(100))
  .addNumberOption(opt => opt.setName('ratio').setDescription('...'))
  .addBooleanOption(opt => opt.setName('flag').setDescription('...'))
  .addUserOption(opt => opt.setName('user').setDescription('...'))
  .addChannelOption(opt => opt.setName('channel').setDescription('...').addChannelTypes(ChannelType.GuildText))
  .addRoleOption(opt => opt.setName('role').setDescription('...'))
  .addMentionableOption(opt => opt.setName('target').setDescription('...'))
  .addAttachmentOption(opt => opt.setName('file').setDescription('...'));
```

## Choices

```javascript
builder.addStringOption(opt =>
  opt.setName('color').setDescription('Pick a color')
    .addChoices(
      { name: 'Red', value: 'red' },
      { name: 'Blue', value: 'blue' },
      { name: 'Green', value: 'green' },
    )
);
```

## Autocomplete

```javascript
// In command definition
builder.addStringOption(opt =>
  opt.setName('query').setDescription('Search').setAutocomplete(true)
);

// Handle autocomplete interaction
client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isAutocomplete()) return;
  const focused = interaction.options.getFocused();
  const choices = ['apple', 'banana', 'cherry']
    .filter(c => c.startsWith(focused))
    .slice(0, 25);
  await interaction.respond(choices.map(c => ({ name: c, value: c })));
});
```

## Subcommands & Groups

```javascript
const settings = new SlashCommandBuilder()
  .setName('settings')
  .setDescription('Manage settings')
  .addSubcommandGroup(group =>
    group.setName('user').setDescription('User settings')
      .addSubcommand(sub =>
        sub.setName('get').setDescription('Get setting')
          .addStringOption(opt => opt.setName('key').setDescription('Setting key').setRequired(true))
      )
      .addSubcommand(sub =>
        sub.setName('set').setDescription('Set setting')
          .addStringOption(opt => opt.setName('key').setDescription('Key').setRequired(true))
          .addStringOption(opt => opt.setName('value').setDescription('Value').setRequired(true))
      )
  );

// Handling
const subGroup = interaction.options.getSubcommandGroup();
const subCmd = interaction.options.getSubcommand();
if (subGroup === 'user' && subCmd === 'get') { ... }
```

## Registering Commands

```javascript
const { REST, Routes } = require('discord.js');
const rest = new REST().setToken(process.env.DISCORD_TOKEN);

// Global commands (up to 1h propagation)
await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });

// Guild commands (instant, for testing)
await rest.put(Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID), { body: commands });
```

## Response Methods

```javascript
// Immediate reply
await interaction.reply('Hello!');
await interaction.reply({ content: 'Secret', flags: MessageFlags.Ephemeral });

// Deferred reply ("Bot is thinking...")
await interaction.deferReply();
await interaction.editReply('Done!');  // within 15 min

// Followup messages
await interaction.reply('First');
await interaction.followUp('Second');
await interaction.followUp({ content: 'Secret followup', flags: MessageFlags.Ephemeral });

// Fetch response as Message object
const response = await interaction.reply({ content: 'Pong!', withResponse: true });
console.log(response.resource.message);

// Or fetch separately
const msg = await interaction.fetchReply();
```

## Parsing Options

```javascript
const user = interaction.options.getUser('target');
const member = interaction.options.getMember('target');
const str = interaction.options.getString('reason');
const num = interaction.options.getInteger('count');
const bool = interaction.options.getBoolean('flag');
const channel = interaction.options.getChannel('channel');
const role = interaction.options.getRole('role');
const attachment = interaction.options.getAttachment('file');
const mentionable = interaction.options.getMentionable('target');
```

## Context Menu Commands

```javascript
const { ContextMenuCommandBuilder, ApplicationCommandType } = require('discord.js');

const userInfo = new ContextMenuCommandBuilder()
  .setName('Get User Info')
  .setType(ApplicationCommandType.User);

const bookmarkMsg = new ContextMenuCommandBuilder()
  .setName('Bookmark')
  .setType(ApplicationCommandType.Message);

// Handling
client.on(Events.InteractionCreate, async (interaction) => {
  if (interaction.isUserContextMenuCommand()) {
    const user = interaction.targetUser;
    await interaction.reply({ content: `${user.tag}: ${user.id}`, flags: MessageFlags.Ephemeral });
  }
  if (interaction.isMessageContextMenuCommand()) {
    const msg = interaction.targetMessage;
    await interaction.reply({ content: `Bookmarked: ${msg.url}`, flags: MessageFlags.Ephemeral });
  }
});
```

## Localization

Use `.setNameLocalizations({ 'es-ES': 'latencia' })` and `.setDescriptionLocalizations({...})`.
Read locale in handler: `interaction.locale` (e.g. `'en-US'`, `'es-ES'`).
