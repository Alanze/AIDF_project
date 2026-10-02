# InsureTutor Demo

InsureTutor is a bilingual RAG demo for answering questions about the insurance product document **FLEXI-ULife Prime Saver**.

This project was built for the AIDF take-home task. The goal is to demonstrate a clear engineering approach rather than a fully polished product: document grounding, citation-aware answers, guardrails, Docker reproducibility, and readable project structure.

## What This Demo Does

- Provides a chat UI for English, Simplified Chinese, and Traditional Chinese questions.
- Retrieves relevant insurance document chunks from `data/processed/chunks.json`.
- Answers with page-level citations from `FLEXI-ULife Prime Saver.pdf`.
- Uses guardrails for out-of-scope questions, missing evidence, and personalized insurance advice.
- Supports a no-key `mock` mode for reproducible local testing.
- Supports Qwen / DashScope through an OpenAI-compatible API.
- Runs with Docker Compose.

## Repository Structure

```text
backend/                  FastAPI backend
  app/api/                HTTP routes
  app/core/               Runtime configuration
  app/guardrails/         Scope, safety, and response validation
  app/ingestion/          PDF extraction helpers
  app/prompts/            System prompt in Markdown
  app/rag/                Knowledge loading, retrieval, and answer generation
  app/schemas/            Pydantic request/response models

frontend/                 Vite + React chat interface
data/raw/                 Source PDF
data/processed/           Curated JSON knowledge chunks and categories
docs/                     Architecture notes, runbook, Qwen setup, sample questions
scripts/                  Utility and verification scripts
Dockerfile                Backend container image
docker-compose.yml        Backend + frontend Docker orchestration
.env.example              Environment variable template
```

## Prerequisites

- Git
- Docker Desktop with the Linux engine running
- Python 3.11+ only if you want to run the verification script from the host
- Node.js only if you want to run the frontend outside Docker

The Docker path is the recommended path for review because it matches the assignment requirement.

## Reproduce With Docker

Clone the repository and enter the project root:

```bash
git clone https://github.com/Alanze/AIDF_project.git
cd AIDF_project
```

Create a local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, the equivalent command is:

```powershell
Copy-Item .env.example .env
```

For the simplest reproducible run, keep:

```env
MODEL_PROVIDER=mock
```

Then start the demo:

```bash
docker compose up --build
```

Open the frontend:

```text
http://localhost:5173
```

Backend health check:

```text
http://localhost:8000/health
```

## Verify The Demo

After Docker is running, execute:

```bash
python scripts/verify_demo.py --mode http
```

Expected result:

```text
OK: Can I skip premium payments?
OK: 4% 派息率是不是保证的？
Verification passed.
```

You can also verify manually in the UI with questions such as:

```text
Can I skip premium payments?
如果现金价值不足会怎样？
4% 派息率是不是保证的？
Should I buy this policy?
```

Expected behavior:

- In-scope answers include citations.
- Chinese questions are answered in Chinese.
- Non-guaranteed rates are described as non-guaranteed.
- Personalized buy/surrender advice is not provided.

## Configure Qwen / DashScope

The demo can call Qwen models through Alibaba Cloud Model Studio / DashScope using the OpenAI-compatible endpoint.

Update `.env`:

```env
MODEL_PROVIDER=qwen
MODEL_NAME=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-your-dashscope-api-key
```

Do not commit `.env`. The repository only commits `.env.example`.

Restart the containers after changing `.env`:

```bash
docker compose down
docker compose up --build
```

More details are documented in `docs/qwen_dashscope_setup.md`.

## Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `MODEL_PROVIDER` | Selects answer generation mode | `mock`, `qwen`, `openai_compatible` |
| `MODEL_NAME` | Model name sent to the provider | `qwen-plus` |
| `LLM_BASE_URL` | OpenAI-compatible API base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `LLM_API_KEY` | Provider API key | `sk-...` |
| `KNOWLEDGE_BASE_PATH` | Path to processed knowledge chunks | `data/processed/chunks.json` |
| `TOP_K` | Number of chunks retrieved before answer generation | `5` |
| `BACKEND_CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173,http://127.0.0.1:5173` |
| `VITE_API_BASE_URL` | Frontend API base URL | `http://localhost:8000` |

## Local Development Without Docker

Docker is preferred, but the services can also run locally.

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

## Architecture

The runtime pipeline is:

1. Receive a user question through the frontend.
2. Detect the user's language.
3. Apply scope and safety guardrails.
4. Retrieve relevant chunks from `data/processed/chunks.json`.
5. Build a grounded prompt using `backend/app/prompts/system_prompt.md`.
6. Generate a schema-shaped answer.
7. Return the answer, caveats, and citations to the UI.

The model is not treated as the source of truth. The insurance document chunks are the source of truth.

## Guardrail Principles

InsureTutor can explain product features, document wording, benefits, risks, fees, exclusions, and conditions. It must not:

- Invent benefits, rates, guarantees, fees, eligibility, exclusions, or policy terms.
- Recommend whether a user should buy, surrender, cancel, or choose the plan.
- Treat assumed rates as guaranteed.
- Answer unrelated questions as if they were supported by the document.
- Provide personalized financial, legal, tax, medical, or insurance advice.

If the retrieved context is insufficient, the assistant should say so and suggest referring to the formal policy document or a qualified professional.

## Current Limitations

- The knowledge base is a curated seed set, not a full production parse of every PDF paragraph.
- Retrieval currently uses transparent lexical scoring over structured JSON.
- Page-level citation is used for this demo; paragraph-level citation would be a production improvement.
- The demo is based on a product brochure and does not replace the formal policy document.

## Useful Documentation

- `docs/runbook.md` - startup, verification, and operational commands
- `docs/qwen_dashscope_setup.md` - Qwen / DashScope setup
- `docs/architecture.md` - architecture notes
- `docs/design_decisions.md` - key engineering decisions
- `docs/sample_questions.md` - suggested evaluation questions
