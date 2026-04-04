# Analytics

Analytics is admin-only, accessible via **Admin Panel > Analytics**. Provides insights into usage patterns, token consumption, and model performance.

To disable the Analytics tab, set `ENABLE_ADMIN_ANALYTICS=False` (requires restart).

## Dashboard Features

### Time Period Selection

Filter all data by: Last 24 hours (hourly granularity), Last 7 days, Last 30 days, Last 90 days, All time. Selection is saved across browser sessions.

### Group Filtering

Filter by user groups using the group dropdown. Useful for department-level reporting, cost allocation, and pilot program monitoring.

### Summary Statistics

- **Total Messages** - Number of assistant responses generated
- **Total Tokens** - Sum of all input and output tokens processed
- **Total Chats** - Number of unique conversations
- **Total Users** - Number of users who sent messages

Analytics counts assistant responses, not user messages.

### Message Timeline Chart

Interactive timeline showing message volume over time by model. Features:
- Hourly or Daily granularity (auto-adjusts based on time period)
- Multi-model visualization (up to 8 models with distinct colors)
- Hover tooltips with exact counts and percentages

### Model Usage Table

| Column | Description |
|---|---|
| **#** | Rank by message count |
| **Model** | Model name with icon |
| **Messages** | Total assistant responses generated |
| **Tokens** | Total tokens (input + output) consumed |
| **%** | Percentage share of total messages |

Sortable columns. Clickable rows open Model Details Modal.

### Model Details Modal

**Overview Tab:**
- Feedback Activity Chart (thumbs up/down history) - 30 days, 1 year, All time views
- Tags - Most common chat tags (top 10)

**Chats Tab** (requires `ENABLE_ADMIN_CHAT_ACCESS` enabled):
- User info, preview, timestamp for conversations using that model
- Click to open shared chat view

### User Activity Table

| Column | Description |
|---|---|
| **#** | Rank by activity |
| **User** | Username with profile picture |
| **Messages** | Total messages sent |
| **Tokens** | Total tokens consumed |

## Token Usage Tracking

Tokens are automatically captured from model responses. Data is normalized across providers (OpenAI, Ollama, llama.cpp, etc.).

Provides per-model token breakdown (input, output, total), total instance-wide usage, and message count correlation.

**Cost Estimation:**

```
Cost = (input_tokens x input_price) + (output_tokens x output_price)
```

Example for GPT-4:
- Input: 1,000,000 tokens x $0.03/1K = $30
- Output: 500,000 tokens x $0.06/1K = $30
- Total: $60

Token accuracy depends on provider: OpenAI/Anthropic provide exact counts; Ollama and llama.cpp report when available; missing data shows as 0.

## Technical Details

### Data Storage

Analytics data is stored in the `chat_message` table containing message content, metadata (model ID, user ID, timestamps), token usage, and relationships. On migration, Open WebUI creates the table, backfills existing messages, and dual-writes new messages.

### Database Indexes

Optimized indexes on: `chat_id`, `user_id`, `model_id`, `created_at`, plus composite indexes.

### API Endpoints

**Dashboard:**

```
GET /api/v1/analytics/summary
GET /api/v1/analytics/models
GET /api/v1/analytics/users
GET /api/v1/analytics/messages
GET /api/v1/analytics/daily
GET /api/v1/analytics/tokens
```

**Model Detail:**

```
GET /api/v1/analytics/models/{model_id}/chats
GET /api/v1/analytics/models/{model_id}/overview
```

**Common Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `start_date` | int | Unix timestamp (epoch seconds) - start of range |
| `end_date` | int | Unix timestamp (epoch seconds) - end of range |
| `group_id` | string | Filter to a specific user group (optional) |

All endpoints require admin authentication:

```bash
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  "https://your-instance.com/api/v1/analytics/summary?group_id=abc123"
```

Export data via API:

```bash
curl -H "Authorization: Bearer TOKEN" \
  "https://instance.com/api/v1/analytics/summary?start_date=1704067200&end_date=1706745600" \
  > analytics_export.json
```

## Privacy & Data

**Tracked:** Message timestamps/counts, token usage per message, model IDs, user IDs, chat IDs, message relationships.

**Not tracked/displayed in dashboard:** Message content, external sharing, individual message content outside the database.

**Retention:** Follows instance chat retention policy. Deleting a chat removes analytics data; deleting a user disassociates their messages.
