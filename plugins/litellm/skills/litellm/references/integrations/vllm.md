# vLLM Integration

Use LiteLLM to proxy requests to self-hosted vLLM inference servers.

## Provider Prefix

Use `hosted_vllm/` (preferred). The `openai/` prefix also works (generic OpenAI-compatible). The `vllm/` prefix is **deprecated**.

## Config

```yaml
model_list:
  - model_name: my-vllm-model
    litellm_params:
      model: hosted_vllm/facebook/opt-125m
      api_base: http://vllm-server:8000
      api_key: optional-key
```

Environment variables (alternative to per-model config):
```
HOSTED_VLLM_API_BASE=http://vllm-server:8000
HOSTED_VLLM_API_KEY=optional-key
```

## Multiple vLLM Servers

```yaml
model_list:
  - model_name: llama
    litellm_params:
      model: hosted_vllm/meta-llama/Llama-3-70b
      api_base: http://vllm-1:8000
  - model_name: llama
    litellm_params:
      model: hosted_vllm/meta-llama/Llama-3-70b
      api_base: http://vllm-2:8000

router_settings:
  routing_strategy: "least-busy"
```

LiteLLM load-balances across deployments with the same `model_name`.

## Supported Endpoints

- `/chat/completions`
- `/completions`
- `/embeddings`
- `/rerank`
- `/audio/transcriptions`

## Features

- **Reasoning effort**: `reasoning_effort: "high"` parameter supported
- **Video URL support**: Pass video URLs in messages
- **Batch completions**: Supported via vLLM batch API
- **Streaming**: Fully supported

## Kubernetes Example

```yaml
model_list:
  - model_name: codellama
    litellm_params:
      model: hosted_vllm/codellama/CodeLlama-34b-Instruct-hf
      api_base: http://vllm.vllm-ns.svc.cluster.local:8000
```
