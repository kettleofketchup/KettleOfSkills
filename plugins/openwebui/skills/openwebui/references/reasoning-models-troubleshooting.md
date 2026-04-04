# Reasoning Models - Streaming, API & Troubleshooting

## Streaming vs Non-Streaming

### Streaming Mode (Default)

In streaming mode (`stream: true`), Open WebUI processes tokens as they arrive and can detect reasoning blocks in real-time. This generally works well without additional configuration.

### Non-Streaming Mode

In non-streaming mode (`stream: false`), the entire response is returned at once. **This is where most parsing issues occur** because:

1. The response arrives as a single block of text
2. Without the reasoning parser, no post-processing separates the `<think>` content
3. The raw response is displayed as-is

If you're using non-streaming requests (via API or certain configurations), **the reasoning parser is essential** for proper thinking block separation.

## API Usage

When using the Open WebUI API with reasoning models:

```json
{
  "model": "qwen3:32b",
  "messages": [
    {"role": "user", "content": "Solve: What is 234 * 567?"}
  ],
  "stream": true
}
```

**Recommendation:** Use `"stream": true` for the most reliable reasoning block parsing.

## Troubleshooting

### Thinking Content Merged with Final Answer

**Symptom:** When using a reasoning model, the entire response (including `<think>...</think>` blocks) is displayed as the final answer, instead of being separated into a hidden/collapsible thinking section.

**Expected behavior:** The thinking content should be hidden or collapsible, with only the final answer visible.

### For Ollama Users

The most common cause is that Ollama is not configured with the correct **reasoning parser**. When running Ollama, you need to specify the `--reasoning-parser` flag to enable proper parsing of thinking blocks.

#### Step 1: Configure the Reasoning Parser

When starting Ollama, add the `--reasoning-parser` flag:

```bash
# For DeepSeek-R1 style reasoning (recommended for most models)
ollama serve --reasoning-parser deepseek_r1

# Alternative parsers (if the above doesn't work for your model)
ollama serve --reasoning-parser qwen3
ollama serve --reasoning-parser deepseek_v3
```

For most reasoning models, including Qwen3 and DeepSeek variants, use `--reasoning-parser deepseek_r1`. This parser handles the standard `<think>...</think>` format used by most reasoning models.

#### Step 2: Restart Ollama

After adding the flag, restart the Ollama service:

```bash
# Stop Ollama
# On Linux/macOS:
pkill ollama

# On Windows (PowerShell):
Stop-Process -Name ollama -Force

# Start with the reasoning parser
ollama serve --reasoning-parser deepseek_r1
```

#### Step 3: Verify in Open WebUI

1. Go to Open WebUI and start a new chat with your reasoning model
2. Ask a question that requires reasoning (e.g., a math problem or logic puzzle)
3. The response should now show the thinking content in a collapsible section

### Available Reasoning Parsers

| Parser | Description | Use Case |
|--------|-------------|----------|
| `deepseek_r1` | DeepSeek R1 format | Most reasoning models, including Qwen3 |
| `deepseek_v3` | DeepSeek V3 format | Some DeepSeek variants |
| `qwen3` | Qwen3-specific format | If `deepseek_r1` doesn't work with Qwen |

### Troubleshooting Checklist

#### 1. Verify Ollama Is Running with Reasoning Parser

Check if Ollama was started with the correct flag:

```bash
# Check the Ollama process
ps aux | grep ollama
# or on Windows:
Get-Process -Name ollama | Format-List *
```

Look for `--reasoning-parser` in the command line arguments.

#### 2. Check Model Compatibility

Not all models output reasoning in the same format. Verify your model's documentation for:

- What tags it uses for thinking content (e.g., `<think>`, `<reasoning>`, etc.)
- Whether it requires specific prompting to enable thinking mode

#### 3. Test with Streaming Enabled

If non-streaming isn't working, try enabling streaming in your chat:

1. Go to **Chat Controls** (sidebar)
2. Ensure streaming is enabled (this is the default)
3. Test the model again

#### 4. Check Open WebUI Version

Ensure you're running the latest version of Open WebUI, as reasoning model support continues to improve:

```bash
docker pull ghcr.io/open-webui/open-webui:main
```

#### 5. Verify the Model Response Format

Use the Ollama CLI directly to check what format your model outputs:

```bash
ollama run your-model:tag "Explain step by step: What is 15 + 27?"
```

Look for `<think>` tags in the output. If they're not present, the model may require specific system prompts to enable thinking mode.

### Reasoning Lost Between Tool Calls

**Symptom:** The model seems to "forget" what it was thinking about after a tool call completes.

**Possible Causes:**
1. The model doesn't output reasoning in a captured format (`reasoning_content`, `reasoning`, or `thinking` delta fields)
2. The model uses text-based thinking tags that aren't being parsed as reasoning blocks

**Solution:** Check if your model outputs reasoning through:
- Structured delta fields (`reasoning_content`, `reasoning`, `thinking`)
- Text-based tags that Open WebUI detects (ensure reasoning tag detection is enabled)

### Anthropic Extended Thinking Not Working with Tool Calls

**Symptom:** Using Anthropic's Claude models with extended thinking enabled, but tool calls fail with errors like:

```
Expected `thinking` or `redacted_thinking`, but found `text`. When `thinking` is enabled,
a final `assistant` message must start with a thinking block.
```

**Cause:** This is a fundamental architectural difference. Open WebUI follows the **OpenAI Chat Completions API standard** and does not natively support Anthropic's proprietary API format. Anthropic's extended thinking requires structured content blocks with `{"type": "thinking"}` or `{"type": "redacted_thinking"}`, which are Anthropic-specific formats.

Open WebUI serializes reasoning as text wrapped in tags (e.g., `<think>...</think>`) inside the message content field. This works with OpenAI-compatible APIs but does not satisfy Anthropic's requirement for structured thinking blocks.

**Workarounds:**

1. **Use a Pipe Function**: Create a custom pipe function that converts Open WebUI's text-based thinking format to Anthropic's structured thinking blocks before sending requests to the Anthropic API.
2. **Disable Extended Thinking**: If you don't need extended thinking for tool-calling workflows, disable it to avoid the format mismatch.

This limitation applies specifically to combining Anthropic's extended thinking with tool calls. Extended thinking works without tool calls, and tool calls work without extended thinking -- the issue only occurs when using both features together via the Anthropic API.

### Stateful Reasoning Models (GPT-5.2, etc.)

**Symptom:** Using a model that hides its reasoning (stateful/internal reasoning), and reasoning is not being preserved.

**Cause:** Some newer models keep their reasoning internal and don't expose it in the API response. Open WebUI can only preserve reasoning that is actually returned by the model.

**Behavior:** If the model returns a reasoning summary instead of full reasoning content, that summary is what gets preserved and sent back.

## Frequently Asked Questions

### Why is the thinking block showing as raw text?
If the model uses tags that are not in the default list and have not been configured in `reasoning_tags`, Open WebUI will treat them as regular text. Fix this by adding the correct tags to the `reasoning_tags` parameter in the Model Settings or Chat Controls.

### Does the model see its own thinking?

**Yes.** Reasoning content is preserved and sent back to the model in both scenarios:

- **Within the same turn (during tool calls)**: When a model makes tool calls, Open WebUI preserves the reasoning content and sends it back to the API as part of the assistant message.
- **Across different turns**: When building messages for subsequent requests, Open WebUI serializes reasoning content from previous turns with its original tags and includes it in the assistant message's `content` field.

### How is reasoning sent during tool calls?

Reasoning is serialized as text with its original tags and included in the assistant message's `content` field. This text-based format works with most OpenAI-compatible providers. However, some providers (like Anthropic) may expect structured thinking content blocks in a specific format.

