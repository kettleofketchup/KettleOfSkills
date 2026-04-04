# Media Generation Reference

## Image Generation

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_IMAGE_GENERATION` | `false` | Enable image gen |
| `IMAGE_GENERATION_ENGINE` | `openai` | `openai`, `comfyui`, `automatic1111`, `gemini` |
| `IMAGE_GENERATION_MODEL` | `dall-e-3` | Model name |
| `IMAGE_SIZE` | `512x512` | Default size |
| `IMAGE_STEPS` | `50` | Generation steps |

### OpenAI / DALL-E
```yaml
environment:
  ENABLE_IMAGE_GENERATION: true
  IMAGE_GENERATION_ENGINE: openai
  IMAGES_OPENAI_API_BASE_URL: https://api.openai.com/v1
  IMAGES_OPENAI_API_KEY: sk-xxx
  IMAGE_GENERATION_MODEL: dall-e-3
```

### AUTOMATIC1111 (Stable Diffusion)
```yaml
environment:
  ENABLE_IMAGE_GENERATION: true
  IMAGE_GENERATION_ENGINE: automatic1111
  AUTOMATIC1111_BASE_URL: http://host.docker.internal:7860
  AUTOMATIC1111_API_AUTH: user:password  # if auth enabled
```
Launch A1111 with `--api` flag. Enable `--listen` for network access.

### ComfyUI
```yaml
environment:
  ENABLE_IMAGE_GENERATION: true
  IMAGE_GENERATION_ENGINE: comfyui
  COMFYUI_BASE_URL: http://host.docker.internal:8188
  COMFYUI_API_KEY: your-key  # if auth required
```
Upload workflow JSON via Admin Panel > Settings > Images > ComfyUI.

### Gemini
```yaml
environment:
  ENABLE_IMAGE_GENERATION: true
  IMAGE_GENERATION_ENGINE: gemini
```
Uses configured Gemini API connection.

### Image Router
Routes image generation requests to different backends based on model selection. Configure via Admin Panel > Settings > Images.

### Usage
- Enable "Image Generation" capability per model
- Users type image generation prompts naturally
- Or use URL param: `/?image-generation=true`

---

## Speech-to-Text (STT)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_STT_ENGINE` | (empty) | `""` (local Whisper), `openai`, `web` |
| `AUDIO_STT_MODEL` | `whisper-1` | STT model name |
| `AUDIO_STT_OPENAI_API_BASE_URL` | `${OPENAI_API_BASE_URL}` | STT API URL |
| `AUDIO_STT_OPENAI_API_KEY` | `${OPENAI_API_KEY}` | STT API key |
| `WHISPER_MODEL` | `base` | Local Whisper model size |
| `WHISPER_MODEL_DIR` | `${DATA_DIR}/cache/whisper/models` | Model storage |

### Configuration
Admin Panel > Settings > Audio > Speech-to-Text

### Whisper Model Sizes
`tiny`, `base`, `small`, `medium`, `large`, `turbo`

Larger = more accurate but slower and more memory.

---

## Text-to-Speech (TTS)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_TTS_ENGINE` | (empty) | `""`, `openai`, `elevenlabs`, `azure` |
| `AUDIO_TTS_MODEL` | `tts-1` | TTS model |
| `AUDIO_TTS_VOICE` | `alloy` | Default voice |
| `AUDIO_TTS_SPLIT_ON` | `punctuation` | Text splitting |
| `AUDIO_TTS_OPENAI_API_BASE_URL` | `${OPENAI_API_BASE_URL}` | TTS API URL |
| `AUDIO_TTS_OPENAI_API_KEY` | `${OPENAI_API_KEY}` | TTS API key |

### OpenAI TTS
```yaml
environment:
  AUDIO_TTS_ENGINE: openai
  AUDIO_TTS_OPENAI_API_BASE_URL: https://api.openai.com/v1
  AUDIO_TTS_OPENAI_API_KEY: sk-xxx
  AUDIO_TTS_MODEL: tts-1
  AUDIO_TTS_VOICE: alloy
```
Voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

### OpenAI Edge TTS (Free)
```yaml
services:
  openai-edge-tts:
    image: travisvn/openai-edge-tts:latest
    ports: ["5050:5050"]
    environment:
      - DEFAULT_VOICE=en-US-AvaNeural
      - DEFAULT_LANGUAGE=en-US
```
Set TTS API URL to `http://openai-edge-tts:5050/v1`

### Kokoro Web (Free, Local)
```yaml
services:
  kokoro-web:
    image: ghcr.io/nicholasgasior/kokoro-web:latest
    ports: ["7860:7860"]
    volumes:
      - kokoro-web:/app/cache
```
Set TTS API URL to `http://kokoro-web:7860/v1`

### OpenedAI Speech (Local)
```yaml
services:
  openedai-speech:
    image: ghcr.io/matatonic/openedai-speech
    ports: ["8000:8000"]
    volumes:
      - openedai-speech:/app/voices
```
Set TTS API URL to `http://openedai-speech:8000/v1`

### Per-Model Voice
Set different TTS voices per model via Workspace > Models > Edit > TTS Voice for distinct AI personas.
