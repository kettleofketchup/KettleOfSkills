---
last_updated: "2026-03-18"
description: discord.js component builders — ButtonBuilder, SelectMenuBuilders, ModalBuilder, TextInputBuilder, LabelBuilder, ActionRowBuilder
---

# discord.js Components

Docs: https://discord.js.org | Guide: https://discordjs.guide

## Buttons (ButtonBuilder)

```javascript
const { ButtonBuilder, ButtonStyle, ActionRowBuilder } = require('discord.js');

const confirm = new ButtonBuilder()
  .setCustomId('confirm')
  .setLabel('Confirm')
  .setStyle(ButtonStyle.Success);

const cancel = new ButtonBuilder()
  .setCustomId('cancel')
  .setLabel('Cancel')
  .setStyle(ButtonStyle.Secondary);

const link = new ButtonBuilder()
  .setLabel('Documentation')
  .setURL('https://discord.js.org')
  .setStyle(ButtonStyle.Link);

const row = new ActionRowBuilder().addComponents(confirm, cancel, link);
await interaction.reply({ content: 'Are you sure?', components: [row] });
```

**ButtonStyle enum:** `Primary` (blue), `Secondary` (grey), `Success` (green), `Danger` (red), `Link` (grey+icon)

Additional methods: `.setEmoji('emoji_id')`, `.setDisabled(true)`

## Handling Button Clicks

```javascript
const { Events } = require('discord.js');

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isButton()) return;

  if (interaction.customId === 'confirm') {
    await interaction.reply({ content: 'Confirmed!', flags: MessageFlags.Ephemeral });
  } else if (interaction.customId === 'cancel') {
    await interaction.update({ content: 'Cancelled', components: [] });
  }
});
```

## Select Menus

### StringSelectMenuBuilder

```javascript
const { StringSelectMenuBuilder, StringSelectMenuOptionBuilder } = require('discord.js');

const select = new StringSelectMenuBuilder()
  .setCustomId('starter')
  .setPlaceholder('Make a selection!')
  .setMinValues(1)
  .setMaxValues(1)
  .addOptions(
    new StringSelectMenuOptionBuilder()
      .setLabel('Bulbasaur')
      .setDescription('Grass/Poison type')
      .setValue('bulbasaur')
      .setEmoji('🌿'),
    new StringSelectMenuOptionBuilder()
      .setLabel('Charmander')
      .setValue('charmander')
      .setDefault(true),
  );

const row = new ActionRowBuilder().addComponents(select);
await interaction.reply({ content: 'Choose starter:', components: [row] });
```

### Auto-populated Select Menus

```javascript
const { UserSelectMenuBuilder, RoleSelectMenuBuilder,
        ChannelSelectMenuBuilder, MentionableSelectMenuBuilder,
        ChannelType } = require('discord.js');

// User select
const userSelect = new UserSelectMenuBuilder()
  .setCustomId('users')
  .setPlaceholder('Select users')
  .setMinValues(1)
  .setMaxValues(5);

// Channel select with filter
const channelSelect = new ChannelSelectMenuBuilder()
  .setCustomId('channel')
  .setPlaceholder('Pick a channel')
  .setChannelTypes(ChannelType.GuildText, ChannelType.GuildVoice);
```

### Handling Select Interactions

```javascript
client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isStringSelectMenu()) return;
  if (interaction.customId === 'starter') {
    await interaction.reply(`You chose: ${interaction.values.join(', ')}`);
  }
});
// Also: isUserSelectMenu(), isRoleSelectMenu(), isChannelSelectMenu(), isMentionableSelectMenu()
```

## Modals (ModalBuilder)

```javascript
const { ModalBuilder, TextInputBuilder, TextInputStyle, LabelBuilder } = require('discord.js');

const modal = new ModalBuilder()
  .setCustomId('feedbackModal')
  .setTitle('Submit Feedback');

const nameInput = new TextInputBuilder()
  .setCustomId('nameInput')
  .setStyle(TextInputStyle.Short)
  .setPlaceholder('Your name');

const nameLabel = new LabelBuilder()
  .setLabel('Your Name')
  .setDescription('How should we address you?')
  .setTextInputComponent(nameInput);

const feedbackInput = new TextInputBuilder()
  .setCustomId('feedbackInput')
  .setStyle(TextInputStyle.Paragraph)
  .setPlaceholder('Enter your feedback...')
  .setMinLength(10)
  .setMaxLength(1000)
  .setRequired(true);

const feedbackLabel = new LabelBuilder()
  .setLabel('Feedback')
  .setTextInputComponent(feedbackInput);

modal.addLabelComponents(nameLabel, feedbackLabel);
await interaction.showModal(modal);
```

**TextInputStyle enum:** `Short` (single-line), `Paragraph` (multi-line)

Additional TextInput methods: `.setValue('default')`, `.setRequired(true)`, `.setId(1)`

### Handling Modal Submissions

```javascript
client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isModalSubmit()) return;
  if (interaction.customId === 'feedbackModal') {
    const name = interaction.fields.getTextInputValue('nameInput');
    const feedback = interaction.fields.getTextInputValue('feedbackInput');
    await interaction.reply({ content: `Thanks ${name}!`, flags: MessageFlags.Ephemeral });
  }
});
```

Modal submit also supports: `getStringSelectValues()`, `getUploadedFiles()`

### Modal with Select Menus

```javascript
const select = new StringSelectMenuBuilder()
  .setCustomId('priority')
  .setPlaceholder('Priority level')
  .setRequired(true)
  .addOptions(
    new StringSelectMenuOptionBuilder().setLabel('Low').setValue('low'),
    new StringSelectMenuOptionBuilder().setLabel('High').setValue('high'),
  );

const label = new LabelBuilder()
  .setLabel('Priority')
  .setStringSelectMenuComponent(select);

modal.addLabelComponents(label);
```

### FileUploadBuilder (Modals)

```javascript
const upload = new FileUploadBuilder()
  .setCustomId('attachment').setMinValues(1).setMaxValues(3).setRequired(true);
const uploadLabel = new LabelBuilder().setLabel('Upload Files').setFileUploadComponent(upload);
modal.addLabelComponents(uploadLabel);
```

## Disabling Components After Use

```javascript
const row = ActionRowBuilder.from(interaction.message.components[0]);
row.components.forEach(c => c.setDisabled(true));
await interaction.update({ components: [row] });
```

## Key Constraints

- `showModal()` must be first response (cannot defer then show modal)
- Max 5 top-level components per modal
- TextInputStyle: `Short` (single-line), `Paragraph` (multi-line)
