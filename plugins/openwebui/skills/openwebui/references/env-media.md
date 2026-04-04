# Open WebUI Environment Variables: Audio & Image Generation

## Speech-to-Text (Whisper - Local)

| Variable | Type | Default | Description |
|---|---|---|---|
| `WHISPER_MODEL` | str | `base` | Whisper model: `tiny`, `base`, `small`, `medium`, `large`. PersistentConfig. |
| `WHISPER_MODEL_DIR` | str | `${DATA_DIR}/cache/whisper/models` | Whisper model storage directory. |
| `WHISPER_COMPUTE_TYPE` | str | `int8` (CPU) / `float16` (CUDA) | Compute type. Use `float16` for GPU. Options: `int8`, `float16`, `int8_float16`, `float32`. |
| `WHISPER_VAD_FILTER` | bool | `False` | Voice Activity Detection filter. |
| `WHISPER_MODEL_AUTO_UPDATE` | bool | `False` | Auto-update Whisper model. |
| `WHISPER_LANGUAGE` | str | `None` | ISO 639-1 language code. Auto-detects by default. |
| `WHISPER_MULTILINGUAL` | bool | `False` | Use multilingual model vs English-only. |

## Speech-to-Text (External Engines)

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUDIO_STT_ENGINE` | str | `''` | STT engine: empty (local Whisper), `openai`, `deepgram`, `azure`, `mistral`. PersistentConfig. |
| `AUDIO_STT_MODEL` | str | `whisper-1` | STT model for OpenAI-compatible endpoints. PersistentConfig. |
| `AUDIO_STT_OPENAI_API_BASE_URL` | str | `$OPENAI_API_BASE_URL` | OpenAI STT base URL. PersistentConfig. |
| `AUDIO_STT_OPENAI_API_KEY` | str | `$OPENAI_API_KEY` | OpenAI STT API key. PersistentConfig. |
| `AUDIO_STT_SUPPORTED_CONTENT_TYPES` | str | `None` | Comma-separated supported audio MIME types. PersistentConfig. |

### Azure STT

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUDIO_STT_AZURE_API_KEY` | str | `None` | Azure STT API key. PersistentConfig. |
| `AUDIO_STT_AZURE_REGION` | str | `None` | Azure region. PersistentConfig. |
| `AUDIO_STT_AZURE_LOCALES` | str | `None` | Azure STT locales. PersistentConfig. |
| `AUDIO_STT_AZURE_BASE_URL` | str | `None` | Custom Azure STT endpoint. PersistentConfig. |
| `AUDIO_STT_AZURE_MAX_SPEAKERS` | int | `3` | Max speakers for diarization. PersistentConfig. |

### Deepgram / Mistral STT

| Variable | Type | Default | Description |
|---|---|---|---|
| `DEEPGRAM_API_KEY` | str | `None` | Deepgram API key. PersistentConfig. |
| `AUDIO_STT_MISTRAL_API_KEY` | str | `None` | Mistral STT API key. PersistentConfig. |
| `AUDIO_STT_MISTRAL_API_BASE_URL` | str | `https://api.mistral.ai/v1` | Mistral STT base URL. PersistentConfig. |
| `AUDIO_STT_MISTRAL_USE_CHAT_COMPLETIONS` | bool | `False` | Use chat completions endpoint for Mistral STT. PersistentConfig. |

## Text-to-Speech

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUDIO_TTS_ENGINE` | str | `''` | TTS engine: empty (disables backend TTS, browser-only), `openai`, `elevenlabs`, `azure`, `transformers`. PersistentConfig. |
| `AUDIO_TTS_MODEL` | str | `tts-1` | TTS model. PersistentConfig. |
| `AUDIO_TTS_VOICE` | str | `alloy` | Default TTS voice. PersistentConfig. |
| `AUDIO_TTS_SPLIT_ON` | str | `punctuation` | TTS text splitting. PersistentConfig. |
| `AUDIO_TTS_API_KEY` | str | - | API key for ElevenLabs/Azure TTS. PersistentConfig. |

### OpenAI TTS

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUDIO_TTS_OPENAI_API_BASE_URL` | str | `$OPENAI_API_BASE_URL` | OpenAI TTS base URL. PersistentConfig. |
| `AUDIO_TTS_OPENAI_API_KEY` | str | `$OPENAI_API_KEY` | OpenAI TTS API key. PersistentConfig. |
| `AUDIO_TTS_OPENAI_PARAMS` | str (JSON) | `{}` | Extra TTS params (e.g., `{"speed": 1.0}`). PersistentConfig. |

### Azure TTS

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUDIO_TTS_AZURE_SPEECH_REGION` | str | - | Azure TTS region. PersistentConfig. |
| `AUDIO_TTS_AZURE_SPEECH_OUTPUT_FORMAT` | str | `audio-24khz-160kbitrate-mono-mp3` | Azure TTS output format. PersistentConfig. |
| `AUDIO_TTS_AZURE_SPEECH_BASE_URL` | str | `None` | Custom Azure Speech endpoint. PersistentConfig. |

### ElevenLabs TTS

| Variable | Type | Default | Description |
|---|---|---|---|
| `ELEVENLABS_API_BASE_URL` | str | `https://api.elevenlabs.io` | ElevenLabs API URL. Supports EU residency endpoints. PersistentConfig. |

### Voice Mode

| Variable | Type | Default | Description |
|---|---|---|---|
| `VOICE_MODE_PROMPT_TEMPLATE` | str | default | Custom system prompt for voice mode. PersistentConfig. |

## Image Generation

### General Settings

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_IMAGE_GENERATION` | bool | `False` | Enables image generation. PersistentConfig. |
| `ENABLE_IMAGE_PROMPT_GENERATION` | bool | `True` | Auto-enhance prompts for better results. PersistentConfig. |
| `IMAGE_GENERATION_ENGINE` | str | `openai` | Engine: `openai`, `comfyui`, `automatic1111`, `gemini`. PersistentConfig. |
| `IMAGE_GENERATION_MODEL` | str | `''` | Default model (e.g., `dall-e-3`). PersistentConfig. |
| `IMAGE_SIZE` | str | `512x512` | Default image size (WxH). Set `auto` for compatible models. PersistentConfig. |
| `IMAGE_STEPS` | int | `50` | Iteration steps (ComfyUI/AUTOMATIC1111). PersistentConfig. |

### Image Editing

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_IMAGE_EDIT` | bool | `True` | Enable image editing. PersistentConfig. |
| `IMAGE_EDIT_ENGINE` | str | `openai` | Edit engine: `openai`, `gemini`, `comfyui`. PersistentConfig. |
| `IMAGE_EDIT_MODEL` | str | `''` | Edit model (e.g., `dall-e-2`). PersistentConfig. |
| `IMAGE_EDIT_SIZE` | str | `''` | Output dimensions. Empty preserves original. PersistentConfig. |

### OpenAI DALL-E

| Variable | Type | Default | Description |
|---|---|---|---|
| `IMAGES_OPENAI_API_BASE_URL` | str | `$OPENAI_API_BASE_URL` | DALL-E API URL. PersistentConfig. |
| `IMAGES_OPENAI_API_KEY` | str | `$OPENAI_API_KEY` | DALL-E API key. PersistentConfig. |
| `IMAGES_OPENAI_API_VERSION` | str | `$OPENAI_API_VERSION` | Azure OpenAI `api-version`. PersistentConfig. |
| `IMAGES_OPENAI_API_PARAMS` | str (JSON) | `{}` | Extra params (e.g., `{"quality":"hd"}`). PersistentConfig. |

### Gemini

| Variable | Type | Default | Description |
|---|---|---|---|
| `IMAGES_GEMINI_API_BASE_URL` | str | `$GEMINI_API_BASE_URL` | Gemini image API URL. PersistentConfig. |
| `IMAGES_GEMINI_API_KEY` | str | `$GEMINI_API_KEY` | Gemini API key. PersistentConfig. |
| `IMAGES_GEMINI_ENDPOINT_METHOD` | str | `''` | `predict` (Imagen) or `generateContent` (Gemini 2.5+). PersistentConfig. |

### ComfyUI

| Variable | Type | Default | Description |
|---|---|---|---|
| `COMFYUI_BASE_URL` | str | `''` | ComfyUI API URL. PersistentConfig. |
| `COMFYUI_API_KEY` | str | `''` | ComfyUI auth key. PersistentConfig. |
| `COMFYUI_WORKFLOW` | str (JSON) | default workflow | ComfyUI workflow. Must use "Save (API Format)". PersistentConfig. |

### AUTOMATIC1111

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUTOMATIC1111_BASE_URL` | str | `''` | A1111 API URL. PersistentConfig. |
| `AUTOMATIC1111_API_AUTH` | str | - | Auth credentials (username:password). PersistentConfig. |
