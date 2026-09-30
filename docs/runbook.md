# Runbook

This runbook separates the demo into four operational layers: model configuration, backend API, frontend UI, and verification harness.

## 1. Model Configuration

For no-key local testing, keep:

```env
MODEL_PROVIDER=mock
```

For Qwen through DashScope:

```env
MODEL_PROVIDER=qwen
MODEL_NAME=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-your-dashscope-key
```

Keep real keys in `.env`; do not commit them.

## 2. Docker Start

From the project root:

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

Backend health endpoint:

```text
http://localhost:8000/health
```

## 3. Local Development Start

Backend:

```bash
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## 4. Verification Harness

After the backend is running:

```bash
python scripts/verify_demo.py --mode http
```

To test without starting a server, after installing backend dependencies:

```bash
python scripts/verify_demo.py --mode in-process
```

Expected result:

```text
OK: Can I skip premium payments?
OK: 4% 派息率是不是保证的？
Verification passed.
```

## 5. Layered Commit Plan

Future work should be committed in small slices:

1. `ingestion`: PDF extraction and knowledge chunk generation.
2. `rag`: retrieval, ranking, citations, and answer assembly.
3. `guardrails`: scope checks, advice refusal, and schema validation.
4. `api`: FastAPI routes and request/response models.
5. `frontend`: chat UI, citation display, and user feedback states.
6. `harness`: tests, smoke scripts, and evaluation questions.
