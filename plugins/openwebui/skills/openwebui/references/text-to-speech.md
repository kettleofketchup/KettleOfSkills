# Text-to-Speech (TTS) - OpenAI Integration

## Requirements

- An OpenAI API key with access to the Audio API
- Open WebUI installed and running

## Quick Setup (UI)

1. Click your **profile icon** (bottom-left corner)
2. Select **Admin Panel**
3. Click **Settings** > **Audio** tab
4. Configure the following:

| Setting | Value |
|---------|-------|
| **Text-to-Speech Engine** | `OpenAI` |
| **API Base URL** | `https://api.openai.com/v1` |
| **API Key** | Your OpenAI API key |
| **TTS Model** | `tts-1` or `tts-1-hd` |
| **TTS Voice** | Choose from available voices |

5. Click **Save**

## Available Models

| Model | Description | Best For |
|-------|-------------|----------|
| `tts-1` | Standard quality, lower latency | Real-time applications, faster responses |
| `tts-1-hd` | Higher quality audio | Pre-recorded content, premium audio quality |

## Available Voices

OpenAI provides 6 built-in voices:

| Voice | Description |
|-------|-------------|
| `alloy` | Neutral, balanced |
| `echo` | Warm, conversational |
| `fable` | Expressive, British accent |
| `onyx` | Deep, authoritative |
| `nova` | Friendly, upbeat |
| `shimmer` | Soft, gentle |

Try different voices to find the one that best suits your use case. You can preview voices in OpenAI's documentation.

## Per-Model TTS Voice

You can assign a specific TTS voice to individual models, allowing different AI personas to have distinct voices. This is configured in the Model Editor.

### Setting a Model-Specific Voice

1. Go to **Workspace > Models**
2. Click the **Edit** (pencil) icon on the model you want to configure
3. Scroll down to find the **TTS Voice** field
4. Enter the voice name (e.g., `alloy`, `echo`, `shimmer`, `onyx`, `nova`, `fable`)
5. Click **Save**

### Voice Priority

When playing TTS audio, Open WebUI uses the following priority:

1. **Model-specific TTS voice** (if set in Model Editor)
2. **User's personal voice setting** (if configured in user settings)
3. **System default voice** (configured by admin)

This allows admins to give each AI persona a consistent voice while still letting users override with their personal preference when no model-specific voice is set.

### Use Cases

- **Character personas**: Give a "British Butler" model the `fable` voice, while an "Energetic Assistant" uses `nova`
- **Language learning**: Assign appropriate voices for different language tutors
- **Accessibility**: Set clearer voices for models designed for accessibility use cases

## Environment Variables Setup

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - AUDIO_TTS_ENGINE=openai
      - AUDIO_TTS_OPENAI_API_BASE_URL=https://api.openai.com/v1
      - AUDIO_TTS_OPENAI_API_KEY=sk-...
      - AUDIO_TTS_MODEL=tts-1
      - AUDIO_TTS_VOICE=alloy
```

### All TTS Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_TTS_ENGINE` | Set to `openai` | empty |
| `AUDIO_TTS_OPENAI_API_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `AUDIO_TTS_OPENAI_API_KEY` | Your OpenAI API key | empty |
| `AUDIO_TTS_MODEL` | TTS model (`tts-1` or `tts-1-hd`) | `tts-1` |
| `AUDIO_TTS_VOICE` | Voice to use | `alloy` |

### General TTS Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_TTS_ENGINE` | TTS engine: empty (disabled), `openai`, `elevenlabs`, `azure`, `transformers` | empty |
| `AUDIO_TTS_MODEL` | TTS model | `tts-1` |
| `AUDIO_TTS_VOICE` | Default voice | `alloy` |
| `AUDIO_TTS_SPLIT_ON` | Split text on: `punctuation` or `none` | `punctuation` |
| `AUDIO_TTS_API_KEY` | API key for ElevenLabs or Azure TTS | empty |

### Azure TTS Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_TTS_AZURE_SPEECH_REGION` | Azure Speech region | `eastus` |
| `AUDIO_TTS_AZURE_SPEECH_BASE_URL` | Custom Azure Speech base URL (optional) | empty |
| `AUDIO_TTS_AZURE_SPEECH_OUTPUT_FORMAT` | Audio output format | `audio-24khz-160kbitrate-mono-mp3` |

### OpenAI-Compatible TTS Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_TTS_OPENAI_API_BASE_URL` | OpenAI-compatible TTS API base URL | `https://api.openai.com/v1` |
| `AUDIO_TTS_OPENAI_API_KEY` | OpenAI TTS API key | empty |
| `AUDIO_TTS_OPENAI_PARAMS` | Additional JSON params for OpenAI TTS | empty |

## Testing TTS

1. Start a new chat
2. Send a message to any model
3. Click the **speaker icon** on the AI response to hear it read aloud

## Response Splitting

When reading long responses, Open WebUI can split text into chunks before sending them to the TTS engine. This is configured in **Admin Panel > Settings > Audio** under **Response Splitting**.

| Option | Description |
|--------|-------------|
| **Punctuation** (default) | Splits at sentence boundaries: periods (`.`), exclamation marks (`!`), question marks (`?`), and newlines. Best for natural pacing. |
| **Paragraphs** | Splits only at paragraph breaks (double newlines). Results in longer audio chunks. |
| **None** | Sends the entire response as one chunk. May cause delays before audio starts on long responses. |

**Punctuation** mode is recommended for most use cases. It provides the best balance of streaming performance (audio starts quickly) and natural speech pacing.

## Using External TTS Services

When running Open WebUI in Docker with an external TTS service:

```yaml
environment:
  - AUDIO_TTS_ENGINE=openai
  - AUDIO_TTS_OPENAI_API_BASE_URL=http://host.docker.internal:5050/v1
  - AUDIO_TTS_OPENAI_API_KEY=your-api-key
```

Use `host.docker.internal` on Docker Desktop (Windows/Mac) to access services on the host. On Linux, use the host IP or container networking.

## Troubleshooting

### No Audio Plays

1. Check your OpenAI API key is valid and has Audio API access
2. Verify the API Base URL is correct (`https://api.openai.com/v1`)
3. Check browser console (F12) for errors

### Audio Quality Issues

- Switch from `tts-1` to `tts-1-hd` for higher quality
- Note: `tts-1-hd` has slightly higher latency

### Rate Limits

OpenAI has rate limits on the Audio API. If you're hitting limits:
- Consider caching common phrases
- Use `tts-1` instead of `tts-1-hd` (uses fewer tokens)

## Cost Considerations

OpenAI charges per character for TTS. See [OpenAI Pricing](https://platform.openai.com/docs/pricing) for current rates. Note that `tts-1-hd` costs more than `tts-1`.

For a free alternative, consider OpenAI Edge TTS which uses Microsoft's free Edge browser TTS.
