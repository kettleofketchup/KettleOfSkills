# Speech-to-Text (STT) Configuration

Open WebUI supports both local, browser, and remote speech to text.

## Cloud / Remote Speech To Text Providers

| Service | API Key Required |
|---------|------------------|
| Local Whisper (default) | No |
| OpenAI (Whisper API) | Yes |
| Mistral (Voxtral) | Yes |
| Deepgram | Yes |
| Azure | Yes |

**Web API** provides STT via the browser's built-in speech recognition (no API key needed, configured in user settings).

## Configuring Your STT Provider

Navigate to the admin settings, choose Audio, provide an API key and choose a model from the dropdown.

## User-Level Settings

- **STT Settings:** Contains settings related to Speech-to-Text functionality.
- **Speech-to-Text Engine:** Determines the engine used for speech recognition (Default or Web API).

## Using STT

Click on the microphone icon. A live audio waveform will indicate successful voice capture. Click the tick icon to save or the 'x' icon to abort.

## Environment Variables

Most settings can also be configured in the **Admin Panel > Settings > Audio** tab. Environment variables take precedence on startup but can be overridden in the UI.

### Local Whisper

| Variable | Description | Default |
|----------|-------------|---------|
| `WHISPER_MODEL` | Whisper model size | `base` |
| `WHISPER_MODEL_DIR` | Directory to store Whisper model files | `{CACHE_DIR}/whisper/models` |
| `WHISPER_COMPUTE_TYPE` | Compute type for inference | `int8` |
| `WHISPER_LANGUAGE` | ISO 639-1 language code (empty = auto-detect) | empty |
| `WHISPER_MULTILINGUAL` | Use the multilingual Whisper model | `false` |
| `WHISPER_MODEL_AUTO_UPDATE` | Auto-download model updates | `false` |
| `WHISPER_VAD_FILTER` | Enable Voice Activity Detection filter | `false` |

**WHISPER_COMPUTE_TYPE Options:**
- `int8` -- CPU default, fastest but may not work on older GPUs
- `float16` -- **Recommended for CUDA/GPU**
- `int8_float16` -- Hybrid mode (int8 weights, float16 computation)
- `float32` -- Maximum compatibility, slowest

If using the `:cuda` Docker image with an older GPU, set `WHISPER_COMPUTE_TYPE=float16` to avoid errors.

### OpenAI-Compatible STT

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_STT_ENGINE` | STT engine: empty (local Whisper), `openai`, `azure`, `deepgram`, `mistral` | empty |
| `AUDIO_STT_MODEL` | STT model for external providers | empty |
| `AUDIO_STT_OPENAI_API_BASE_URL` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `AUDIO_STT_OPENAI_API_KEY` | OpenAI API key | empty |
| `AUDIO_STT_SUPPORTED_CONTENT_TYPES` | Comma-separated list of supported audio MIME types | empty |

### Azure STT

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_STT_AZURE_API_KEY` | Azure Cognitive Services API key | empty |
| `AUDIO_STT_AZURE_REGION` | Azure region | `eastus` |
| `AUDIO_STT_AZURE_LOCALES` | Comma-separated locales (e.g., `en-US,de-DE`) | auto |
| `AUDIO_STT_AZURE_BASE_URL` | Custom Azure base URL (optional) | empty |
| `AUDIO_STT_AZURE_MAX_SPEAKERS` | Max speakers for diarization | `3` |

### Deepgram STT

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPGRAM_API_KEY` | Deepgram API key | empty |

### Mistral STT

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_STT_MISTRAL_API_KEY` | Mistral API key | empty |
| `AUDIO_STT_MISTRAL_API_BASE_URL` | Mistral API base URL | `https://api.mistral.ai/v1` |
| `AUDIO_STT_MISTRAL_USE_CHAT_COMPLETIONS` | Use chat completions endpoint | `false` |

## OpenAI STT Integration

### Quick Setup (UI)

1. Click your **profile icon** > **Admin Panel** > **Settings** > **Audio** tab
2. Configure:

| Setting | Value |
|---------|-------|
| **Speech-to-Text Engine** | `OpenAI` |
| **API Base URL** | `https://api.openai.com/v1` |
| **API Key** | Your OpenAI API key |
| **STT Model** | `whisper-1` |
| **Supported Content Types** | Leave empty for defaults, or set `audio/wav,audio/mpeg,audio/webm` |

3. Click **Save**

### Available Models

| Model | Description |
|-------|-------------|
| `whisper-1` | OpenAI's Whisper large-v2 model, hosted in the cloud |

### Environment Variables Setup (OpenAI)

```yaml
services:
  open-webui:
    environment:
      - AUDIO_STT_ENGINE=openai
      - AUDIO_STT_OPENAI_API_BASE_URL=https://api.openai.com/v1
      - AUDIO_STT_OPENAI_API_KEY=sk-...
      - AUDIO_STT_MODEL=whisper-1
```

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIO_STT_ENGINE` | Set to `openai` | empty (uses local Whisper) |
| `AUDIO_STT_OPENAI_API_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `AUDIO_STT_OPENAI_API_KEY` | Your OpenAI API key | empty |
| `AUDIO_STT_MODEL` | STT model | `whisper-1` |
| `AUDIO_STT_SUPPORTED_CONTENT_TYPES` | Allowed audio MIME types | `audio/*,video/webm` |

### Supported Audio Formats

By default, Open WebUI accepts `audio/*` and `video/webm`. OpenAI's Whisper API supports: `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`.

### OpenAI vs Local Whisper

| Feature | OpenAI Whisper API | Local Whisper |
|---------|-------------------|---------------|
| **Latency** | Network dependent | Faster for short clips |
| **Cost** | Per-minute pricing | Free (uses your hardware) |
| **Privacy** | Audio sent to OpenAI | Audio stays local |
| **GPU Required** | No | Recommended for speed |
| **Model Options** | `whisper-1` only | tiny, base, small, medium, large |

## Troubleshooting

### "int8 compute type not supported" Error

Set `WHISPER_COMPUTE_TYPE=float16` or `float32`. Switch to the standard Docker image instead of `:cuda` for older GPUs (Maxwell architecture, ~2014-2016). CPU mode often provides comparable performance for Whisper.

### Microphone Not Working

1. Check browser permissions for microphone access
2. Use HTTPS (some browsers require secure connections)
3. Try Chrome (best web audio API support)
4. Ensure you're using HTTPS or localhost

### Poor Recognition Accuracy

- Set language explicitly: `WHISPER_LANGUAGE=en` (ISO 639-1 codes)
- Enable multilingual: `WHISPER_MULTILINGUAL=true` for non-English languages
- Use a larger model: `tiny`, `base`, `small`, `medium`, `large` (larger = more accurate but slower)

### OpenAI STT Issues

- Check your OpenAI API key is valid
- Verify the API Base URL is correct
- Check container logs for error messages
- OpenAI auto-detects language; for forced language, use Local Whisper with `WHISPER_LANGUAGE`

## Cost Considerations

- OpenAI charges per minute of audio. See [OpenAI Pricing](https://platform.openai.com/docs/pricing).
- For free STT, use **Local Whisper** (default) or the browser's **Web API**.
- For GPU issues, set `WHISPER_COMPUTE_TYPE=float16`.
