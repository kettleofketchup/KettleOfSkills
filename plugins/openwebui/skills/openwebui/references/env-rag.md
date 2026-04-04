# Open WebUI Environment Variables: RAG, Embedding, Content Extraction, Web Search

## Content Extraction Engine

| Variable | Type | Default | Description |
|---|---|---|---|
| `CONTENT_EXTRACTION_ENGINE` | str | `''` | Engine: empty (default pypdf), `tika`, `docling`, `external`, `document_intelligence`, `mistral_ocr`, `mineru`. PersistentConfig. Default pypdf has memory leaks -- use Tika/Docling in production. |
| `TIKA_SERVER_URL` | str | `http://localhost:9998` | Apache Tika server URL. PersistentConfig. |
| `DOCLING_SERVER_URL` | str | `http://docling:5001` | Docling server URL. Requires v2.0.0+. PersistentConfig. |
| `DOCLING_API_KEY` | str | `None` | Docling server auth key. PersistentConfig. |
| `DOCLING_PARAMS` | str (JSON) | `{}` | All Docling params: `do_ocr`, `force_ocr`, `ocr_engine` (tesseract/easyocr), `ocr_lang`, `pdf_backend` (dlparse_v4), `table_mode`, `pipeline`, `do_picture_description`. PersistentConfig. |
| `EXTERNAL_DOCUMENT_LOADER_URL` | str | `None` | External document loader URL. PersistentConfig. |
| `EXTERNAL_DOCUMENT_LOADER_API_KEY` | str | `None` | External loader API key. PersistentConfig. |
| `MISTRAL_OCR_API_KEY` | str | `None` | Mistral OCR API key. PersistentConfig. |
| `MISTRAL_OCR_API_BASE_URL` | str | `https://api.mistral.ai/v1` | Mistral OCR base URL. PersistentConfig. |
| `DOCUMENT_INTELLIGENCE_ENDPOINT` | str | `None` | Azure Document Intelligence endpoint. PersistentConfig. |
| `DOCUMENT_INTELLIGENCE_KEY` | str | `None` | Azure Document Intelligence key. PersistentConfig. |
| `DOCUMENT_INTELLIGENCE_MODEL` | str | `None` | Azure Document Intelligence model. PersistentConfig. |
| `MINERU_API_TIMEOUT` | str | `300` | MinerU API timeout (seconds). PersistentConfig. |

## RAG Core Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `RAG_EMBEDDING_ENGINE` | str | `''` | Engine: empty (SentenceTransformers), `ollama`, `openai`, `azure_openai`. PersistentConfig. |
| `RAG_EMBEDDING_MODEL` | str | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model. PersistentConfig. |
| `RAG_TOP_K` | int | `3` | Results to consider for embedding. PersistentConfig. |
| `RAG_TOP_K_RERANKER` | int | `3` | Results for reranker. PersistentConfig. |
| `RAG_RELEVANCE_THRESHOLD` | float | `0.0` | Relevance threshold for reranking. PersistentConfig. |
| `ENABLE_RAG_HYBRID_SEARCH` | bool | `False` | BM25 + ChromaDB ensemble with reranking. PersistentConfig. |
| `RAG_HYBRID_BM25_WEIGHT` | float | `0.5` | BM25 weight (1=keyword only, 0=vector only). PersistentConfig. |
| `ENABLE_RAG_HYBRID_SEARCH_ENRICHED_TEXTS` | bool | `False` | Enriches BM25 with document metadata. PersistentConfig. |
| `RAG_EMBEDDING_MODEL_TRUST_REMOTE_CODE` | bool | `False` | Allow custom Hub models. |
| `RAG_EMBEDDING_MODEL_AUTO_UPDATE` | bool | `True` | Auto-update SentenceTransformer model. |

## Document Processing

| Variable | Type | Default | Description |
|---|---|---|---|
| `CHUNK_SIZE` | int | `1000` | Document chunk size. PersistentConfig. |
| `CHUNK_OVERLAP` | int | `100` | Chunk overlap. PersistentConfig. |
| `CHUNK_MIN_SIZE_TARGET` | int | `0` | Merge chunks smaller than this. Only with markdown splitter. PersistentConfig. |
| `RAG_TEXT_SPLITTER` | str | `character` | Splitter: `character` or `token`. PersistentConfig. |
| `ENABLE_MARKDOWN_HEADER_TEXT_SPLITTER` | bool | `True` | Split by markdown headers first. PersistentConfig. |
| `PDF_EXTRACT_IMAGES` | bool | `False` | OCR extract images from PDFs. PersistentConfig. |
| `PDF_LOADER_MODE` | str | `page` | `page` or `single` (combine all pages). PersistentConfig. |
| `RAG_FILE_MAX_SIZE` | int | - | Max upload size (MB). PersistentConfig. |
| `RAG_FILE_MAX_COUNT` | int | - | Max upload count. PersistentConfig. |
| `RAG_ALLOWED_FILE_EXTENSIONS` | list | `[]` | Allowed extensions (e.g., `["pdf,docx,txt"]`). PersistentConfig. |
| `TIKTOKEN_ENCODING_NAME` | str | `cl100k_base` | TikToken encoding. PersistentConfig. |

## Embedding Engine Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `RAG_EMBEDDING_BATCH_SIZE` | int | `1` | Chunks per API request. Increase only if API supports batching. PersistentConfig. |
| `ENABLE_ASYNC_EMBEDDING` | bool | `True` | Parallel embedding for Ollama/OpenAI. PersistentConfig. |
| `RAG_EMBEDDING_CONCURRENT_REQUESTS` | int | `0` | Max concurrent requests (0=unlimited). PersistentConfig. |
| `RAG_EMBEDDING_TIMEOUT` | int | `None` | Timeout for embedding ops (seconds). |
| `RAG_EMBEDDING_CONTENT_PREFIX` | str | `None` | Prefix for document content (e.g., `search_document: ` for nomic). |
| `RAG_EMBEDDING_QUERY_PREFIX` | str | `None` | Prefix for queries (e.g., `search_query: ` for nomic). |
| `RAG_OPENAI_API_BASE_URL` | str | `$OPENAI_API_BASE_URL` | OpenAI URL for RAG. PersistentConfig. |
| `RAG_OPENAI_API_KEY` | str | `$OPENAI_API_KEY` | OpenAI key for RAG. PersistentConfig. |
| `RAG_OLLAMA_BASE_URL` | str | - | Ollama URL for RAG. PersistentConfig. |
| `RAG_AZURE_OPENAI_BASE_URL` | str | `None` | Azure OpenAI URL for RAG. PersistentConfig. |
| `RAG_AZURE_OPENAI_API_KEY` | str | `None` | Azure OpenAI key for RAG. PersistentConfig. |
| `RAG_AZURE_OPENAI_API_VERSION` | str | `None` | Azure API version. PersistentConfig. |

## Reranking

| Variable | Type | Default | Description |
|---|---|---|---|
| `RAG_RERANKING_ENGINE` | str | `''` | `external` or empty (local CrossEncoder). PersistentConfig. |
| `RAG_RERANKING_MODEL` | str | - | Reranking model. PersistentConfig. |
| `RAG_EXTERNAL_RERANKER_URL` | str | `''` | Full URL for external reranker (include endpoint path). PersistentConfig. |
| `RAG_EXTERNAL_RERANKER_API_KEY` | str | `''` | External reranker API key. PersistentConfig. |
| `RAG_EXTERNAL_RERANKER_TIMEOUT` | str | `''` | Reranker timeout (seconds). PersistentConfig. |
| `RAG_RERANKING_MODEL_TRUST_REMOTE_CODE` | bool | `False` | Allow custom Hub reranking models. |
| `RAG_RERANKING_MODEL_AUTO_UPDATE` | bool | `True` | Auto-update reranking model. |

## Advanced RAG Settings

| Variable | Type | Default | Description |
|---|---|---|---|
| `BYPASS_EMBEDDING_AND_RETRIEVAL` | bool | `False` | Bypass embedding/retrieval entirely. PersistentConfig. |
| `RAG_FULL_CONTEXT` | bool | `False` | Use full document context. PersistentConfig. |
| `RAG_SYSTEM_CONTEXT` | bool | `False` | Inject RAG context into system message (recommended for KV cache). |
| `ENABLE_RAG_LOCAL_WEB_FETCH` | bool | `False` | Allow fetching private/local network URLs (SSRF risk). PersistentConfig. |
| `ENABLE_RETRIEVAL_QUERY_GENERATION` | bool | `True` | Enable retrieval query generation. PersistentConfig. |
| `ENABLE_QUERIES_CACHE` | bool | `False` | Cache generated queries across web search + RAG. Reduces duplicate LLM calls. |

## Web Search

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_WEB_SEARCH` | bool | `False` | Enable web search. PersistentConfig. |
| `WEB_SEARCH_ENGINE` | str | - | Engine: `searxng`, `google_pse`, `brave`, `kagi`, `mojeek`, `duckduckgo`, `tavily`, `jina`, `bing`, `exa`, `perplexity`, `perplexity_search`, `serper`, `serpapi`, etc. PersistentConfig. |
| `WEB_SEARCH_RESULT_COUNT` | int | `3` | Max results to crawl. PersistentConfig. |
| `WEB_SEARCH_CONCURRENT_REQUESTS` | int | `0` | Search engine concurrency (set 1 for Brave free tier). PersistentConfig. |
| `WEB_LOADER_CONCURRENT_REQUESTS` | int | `10` | Page fetch concurrency. PersistentConfig. |
| `WEB_SEARCH_TRUST_ENV` | bool | `False` | Use proxy env vars for web content fetching. PersistentConfig. |
| `WEB_SEARCH_DOMAIN_FILTER_LIST` | list | `[]` | Domain allowlist/blocklist. `!` prefix = block. PersistentConfig. |
| `WEB_FETCH_MAX_CONTENT_LENGTH` | int | `None` | Max chars from fetched URLs. PersistentConfig. |
| `BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL` | bool | `False` | Bypass web search embedding. PersistentConfig. |
| `BYPASS_WEB_SEARCH_WEB_LOADER` | bool | `False` | Use only snippets, skip full page fetch. PersistentConfig. |

### Search Engine API Keys

`SEARXNG_QUERY_URL`, `GOOGLE_PSE_API_KEY`, `GOOGLE_PSE_ENGINE_ID`, `BRAVE_SEARCH_API_KEY`, `KAGI_SEARCH_API_KEY`, `MOJEEK_SEARCH_API_KEY`, `TAVILY_API_KEY`, `JINA_API_KEY`, `BING_SEARCH_V7_SUBSCRIPTION_KEY`, `EXA_API_KEY`, `SERPER_API_KEY`, `SERPAPI_API_KEY`, `BOCHA_SEARCH_API_KEY`, `PERPLEXITY_API_KEY`, `YOUCOM_API_KEY` -- all PersistentConfig.

## Web Loader

| Variable | Type | Default | Description |
|---|---|---|---|
| `WEB_LOADER_ENGINE` | str | `''` | `safe_web` (default), `playwright`, `firecrawl`, `tavily`, `external`. PersistentConfig. |
| `PLAYWRIGHT_WS_URL` | str | `None` | Remote Playwright browser WebSocket URI. PersistentConfig. |
| `FIRECRAWL_API_BASE_URL` | str | `https://api.firecrawl.dev` | Firecrawl API URL. PersistentConfig. |
| `FIRECRAWL_API_KEY` | str | `None` | Firecrawl API key. PersistentConfig. |
| `WEB_LOADER_TIMEOUT` | float | `None` | SafeWebBaseLoader timeout (seconds). PersistentConfig. |

## Google Drive / OneDrive Integration

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_GOOGLE_DRIVE_INTEGRATION` | bool | `False` | Enable Google Drive. PersistentConfig. |
| `GOOGLE_DRIVE_CLIENT_ID` | str | - | Google Drive client ID. PersistentConfig. |
| `GOOGLE_DRIVE_API_KEY` | str | - | Google Drive API key. PersistentConfig. |
| `ENABLE_ONEDRIVE_INTEGRATION` | bool | `False` | Enable OneDrive. PersistentConfig. |
| `ONEDRIVE_CLIENT_ID_PERSONAL` | str | `None` | Personal OneDrive client ID. |
| `ONEDRIVE_CLIENT_ID_BUSINESS` | str | `None` | Work/School OneDrive client ID. |
| `ONEDRIVE_SHAREPOINT_URL` | str | `None` | SharePoint root URL. PersistentConfig. |
| `ONEDRIVE_SHAREPOINT_TENANT_ID` | str | `None` | Azure tenant ID for work/school. PersistentConfig. |

## YouTube Loader

| Variable | Type | Default | Description |
|---|---|---|---|
| `YOUTUBE_LOADER_PROXY_URL` | str | - | Proxy URL for YouTube loader. PersistentConfig. |
| `YOUTUBE_LOADER_LANGUAGE` | str | `en` | Comma-separated language codes for transcriptions. PersistentConfig. |
