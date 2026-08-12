# API Reference — Messages, Files, and SDKs

Messages API, Files API, client SDKs, and error handling.

## Messages API

### Create Message

```bash
POST /v1/messages
```

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "messages": [{ "role": "user", "content": "Explain this code" }]
}
```

With skills:
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "skills": [{ "type": "custom", "custom": { "name": "code-reviewer",
    "description": "Reviews code quality", "instructions": "Check for bugs..." } }],
  "messages": [...]
}
```

### Stream Messages

```json
{ "model": "claude-sonnet-4-5-20250929", "stream": true, "messages": [...] }
```

SSE events: `message_start`, `content_block_delta`, `message_stop`

### Count Tokens

```bash
POST /v1/messages/count_tokens
```

Response: `{ "input_tokens": 15 }`

## Files API

```bash
# Upload (multipart/form-data)
POST /v1/files
curl https://api.anthropic.com/v1/files -H "x-api-key: $ANTHROPIC_API_KEY" \
  -F file=@document.pdf -F purpose=user_upload

# List
GET /v1/files

# Download
GET /v1/files/{file_id}/content

# Delete
DELETE /v1/files/{file_id}
```

## Client SDKs

### TypeScript/JavaScript

```typescript
import Anthropic from '@anthropic-ai/sdk';
const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const message = await client.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude!' }]
});
```

### Python

```python
import anthropic
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
message = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)
```

## Error Handling

### Error Format

```json
{ "type": "error", "error": { "type": "invalid_request_error", "message": "..." } }
```

### Error Types

- `invalid_request_error`: Invalid parameters
- `authentication_error`: Invalid API key
- `permission_error`: Insufficient permissions
- `not_found_error`: Resource not found
- `rate_limit_error`: Rate limit exceeded
- `api_error`: Internal API error
- `overloaded_error`: Server overloaded

### Retry Logic

```typescript
async function withRetry(fn: () => Promise<any>, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try { return await fn(); }
    catch (error) {
      if (error.status === 529 && i < maxRetries - 1) {
        await new Promise(r => setTimeout(r, 1000 * (i + 1)));
        continue;
      }
      throw error;
    }
  }
}
```

## See Also

- Admin/Models/Skills API: `references/api-admin.md`
- SDK docs: https://docs.anthropic.com/api/client-sdks
- Error handling: https://docs.anthropic.com/api/errors
