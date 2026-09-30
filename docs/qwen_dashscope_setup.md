# Qwen / DashScope Setup

This project can call Qwen models through Alibaba Cloud Model Studio / DashScope using the OpenAI-compatible API.

## Recommended Environment

Create a local `.env` from `.env.example` and set:

```env
MODEL_PROVIDER=qwen
MODEL_NAME=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-your-dashscope-key
```

Do not commit `.env`.

## API Key Steps

1. Open Alibaba Cloud Model Studio / Bailian.
2. Go to the API Key page.
3. Select the same region that you want to call from.
4. Create or copy a DashScope API key.
5. Use the matching OpenAI-compatible Base URL for that region.

The common mainland China endpoint is:

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

The API key and Base URL must belong to the same region and billing setup. Otherwise the service can return authentication errors such as 401.

## Model Choice

For this demo, start with:

```env
MODEL_NAME=qwen-plus
```

It is strong enough for bilingual grounded answers and still cheaper than using top-tier models. If you want faster or cheaper responses, try a smaller supported Qwen model available in your Model Studio account.

## Smoke Test With Curl

After the backend is running:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Can I skip premium payments?\"}"
```

If you keep `MODEL_PROVIDER=mock`, this test does not call DashScope. If you set `MODEL_PROVIDER=qwen`, it calls the configured Qwen model.
