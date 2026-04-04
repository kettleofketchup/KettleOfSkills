# Web Search Providers Reference

## Provider Summary Table

| Provider | Engine Value | API Key Env Var | Free Tier |
|----------|-------------|-----------------|-----------|
| Bing | `bing` | `BING_SEARCH_V7_SUBSCRIPTION_KEY` | No (DEPRECATED Aug 2025) |
| Brave | `brave` | `BRAVE_SEARCH_API_KEY` | Yes (1 req/s) |
| DDGS | `ddgs` | None | Yes |
| Exa AI | `exa` | `EXA_API_KEY` | $10 credits |
| Google PSE | `google_pse` | `GOOGLE_PSE_API_KEY` + `GOOGLE_PSE_ENGINE_ID` | No (DEPRECATED) |
| Jina | `jina` | `JINA_API_KEY` | 10M tokens |
| Kagi | `kagi` | `KAGI_SEARCH_API_KEY` | No |
| Mojeek | `mojeek` | `MOJEEK_SEARCH_API_KEY` | No |
| Perplexity | `perplexity` | `PERPLEXITY_API_KEY` | No |
| Perplexity Search | `perplexity_search` | `PERPLEXITY_API_KEY` | No |
| SearchApi | `searchapi` | `SEARCHAPI_API_KEY` | No |
| SearXNG | `searxng` | None (self-hosted) | Yes |
| SerpApi | `serpapi` | `SERPAPI_API_KEY` | No |
| Serper | `serper` | `SERPER_API_KEY` | No |
| Serply | `serply` | `SERPLY_API_KEY` | No |
| Serpstack | `serpstack` | `SERPSTACK_API_KEY` | No |
| Tavily | `tavily` | `TAVILY_API_KEY` | Limited |
| YaCy | `yacy` | None (self-hosted) | Yes |
| Yandex | `yandex` | `YANDEX_WEB_SEARCH_API_KEY` | No |
| You.com | `youcom` | `YOUCOM_API_KEY` | No |
| External | `external` | `EXTERNAL_SEARCH_API_KEY` | N/A |

## Common Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_RAG_WEB_SEARCH` | `false` | Enable web search |
| `RAG_WEB_SEARCH_ENGINE` | `""` | Provider name (see Engine Value above) |
| `RAG_WEB_SEARCH_RESULT_COUNT` | `3` | Number of results |
| `RAG_WEB_SEARCH_CONCURRENT_REQUESTS` | `10` | Max parallel requests |

## Agentic Search vs Traditional RAG

| Feature | Traditional RAG (Default) | Agentic Search (Native Mode) |
|---------|---------------------------|------------------------------|
| Search Decision | System analyzes prompts | Model decides when to search |
| Data Processing | Fetches, chunks, uses Vector DB | Returns snippets directly |
| Link Following | Top result snippets injected | Model uses `fetch_url` for full pages |
| Reasoning | Processes data after injection | Search, read, verify, iterate |

### Enabling Agentic Search
1. Admin Panel > Settings > Web Search -- configure engine
2. Admin Panel > Settings > Models > Enable "Web Search" capability
3. Check "Web Search" under Default Features
4. Set Function Calling to `Native`
5. Use frontier-class model

### Native Tools
- **`search_web`**: Queries engine, returns titles/links/snippets. No RAG/Vector DB.
- **`fetch_url`**: Visits URL, extracts text. Hard limit: 50,000 chars.

## Provider Details

### Brave
```yaml
environment:
  ENABLE_RAG_WEB_SEARCH: True
  RAG_WEB_SEARCH_ENGINE: "brave"
  BRAVE_SEARCH_API_KEY: "YOUR_API_KEY"
  RAG_WEB_SEARCH_CONCURRENT_REQUESTS: 1  # Required for free tier
```

### DDGS (DuckDuckGo)
No API key required. `DDGS_BACKEND`: `auto`, `bing`, `brave`, `duckduckgo`, `google`, `mojeek`, `wikipedia`, `yahoo`, `yandex`

### SearXNG (Self-Hosted)
```yaml
services:
  searxng:
    image: searxng/searxng:latest
    ports: ["8080:8080"]
    volumes: ["./searxng:/etc/searxng:rw"]
  open-webui:
    environment:
      ENABLE_RAG_WEB_SEARCH: True
      RAG_WEB_SEARCH_ENGINE: "searxng"
      SEARXNG_QUERY_URL: "http://searxng:8080/search?q=<query>"
```
JSON format must be enabled in `searxng/settings.yml`:
```yaml
search:
  formats:
    - html
    - json
```

### Jina
Advanced params: `reasoning_effort`, `budget_tokens`, `max_attempts`, `team_size`, domain filtering (`boost_hostnames`/`bad_hostnames`/`only_hostnames`)

### Yandex
```yaml
environment:
  YANDEX_WEB_SEARCH_API_KEY: "KEY"
  YANDEX_WEB_SEARCH_URL: "https://searchapi.api.cloud.yandex.net/v2/web/search"  # optional
  YANDEX_WEB_SEARCH_CONFIG: '{"query": {"searchType": "SEARCH_TYPE_RU"}}'  # optional
```

### External (Custom API)
POST endpoint with `{"query": "...", "count": 5}`, returns `[{"link": "...", "title": "...", "snippet": "..."}]`

### Tavily
Requires `WEBUI_URL` env var to be configured.

## Save Search Results to Knowledge

Action from Community Hub. Click folder+ icon in message toolbar > enter source numbers > select target KB.

| Valve | Default | Purpose |
|-------|---------|---------|
| `max_urls_per_action` | `10` | Max URLs per action |
| `enable_duplicate_check` | `True` | Check existing URLs |
| `default_knowledge_base` | `""` | Default KB name |
| `skip_confirmation` | `False` | Skip dialog |
