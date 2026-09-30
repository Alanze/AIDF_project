# InsureTutor Demo

InsureTutor is a small bilingual RAG demo for answering questions about a specific insurance product document: `FLEXI-ULife Prime Saver`.

The project is designed for the AIDF take-home task. The focus is not a polished production app, but a clear implementation structure: document processing, grounded retrieval, safe answer generation, citations, and Docker-based reproducibility.

## Features

- Chat interface for English and Chinese questions.
- Retrieval over structured insurance document chunks.
- Grounded answers with page-level citations.
- Guardrails for out-of-scope questions, missing evidence, and personalized financial advice.
- Fixed response schema from the backend.
- OpenAI-compatible model adapter for local open-source models such as Ollama.
- No-key `mock` mode for development and Docker smoke tests.

## Project Structure

```text
backend/                FastAPI backend
  app/api/              HTTP routes
  app/guardrails/       Safety and scope checks
  app/ingestion/        PDF extraction and chunk-building helpers
  app/prompts/          System prompt and answer contract
  app/rag/              Knowledge loading, retrieval, generation
  app/schemas/          Pydantic request/response models
frontend/               Vite + React chat UI
data/raw/               Source PDF
data/processed/         Curated JSON knowledge chunks
docs/                   Design notes and sample questions
scripts/                Utility scripts
```

## Quick Start

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Run with Docker:

```bash
docker compose up --build
```

3. Open the app:

```text
http://localhost:5173
```

Backend health check:

```text
http://localhost:8000/health
```

## Using A Local Open-Source Model

The default `.env.example` uses `MODEL_PROVIDER=mock` so the demo can run without downloading a model. To use Ollama or another OpenAI-compatible runtime, set:

```env
MODEL_PROVIDER=openai_compatible
OPENAI_BASE_URL=http://ollama:11434/v1
OPENAI_API_KEY=ollama
MODEL_NAME=qwen2.5:7b-instruct
```

Then make sure the model is available in your runtime, for example:

```bash
ollama pull qwen2.5:7b-instruct
```

## Architecture

The user question goes through this pipeline:

1. Detect the user's language.
2. Run guardrails for scope and unsafe personalized advice.
3. Retrieve relevant knowledge chunks from `data/processed/chunks.json`.
4. Build a prompt containing only retrieved evidence.
5. Generate a schema-shaped answer.
6. Validate the answer and return citations to the UI.

The model is not treated as the source of truth. The insurance PDF-derived knowledge chunks are the source of truth.

## Guardrail Principles

InsureTutor can explain product features, terms, fees, risks, exclusions, and document wording. It must not:

- Invent benefits, rates, guarantees, fees, eligibility, or exclusions.
- Recommend whether a user should buy, surrender, cancel, or choose the plan.
- Treat non-guaranteed rates as guaranteed.
- Answer unrelated questions as if they were in the insurance document.
- Provide legal, tax, medical, or personalized financial advice.

If the provided document does not contain enough evidence, the assistant should say so clearly and suggest checking the policy document or consulting a qualified professional.

## Current Limitations

- The processed knowledge base is a curated seed set rather than a complete production-grade parse of every PDF paragraph.
- Retrieval currently uses transparent lexical scoring over structured JSON. The project is ready for a vector store upgrade.
- The demo is based on a product brochure and does not replace the full policy document.

## Suggested Evaluation Questions

- Can I skip premium payments?
- What is the guaranteed interest rate?
- What happens if the cash value is not enough to cover monthly charges?
- Is the extra bonus guaranteed?
- What are the death benefit options?
- Should I buy this policy for retirement?
- 这份计划可以暂停缴费吗？
- 额外回报是不是保证的？
