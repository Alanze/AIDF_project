# Architecture Notes

## Goal

InsureTutor should answer questions about a specific insurance product document with citations and safety limits.

## Main Design Choice

The system uses structured JSON chunks as the knowledge layer. Each chunk has:

- product name
- category
- section title
- page number
- English and Chinese summaries
- source text
- caveats
- keywords

This makes the RAG layer inspectable. The reviewer can see exactly what evidence the assistant uses.

## Current Retrieval Strategy

The first implementation uses lexical scoring over summaries, source text, categories, and keywords. This is simple and transparent for a take-home demo. A vector store can be added later by embedding the same chunks.

## Model Boundary

The language model is only responsible for phrasing the answer. It should not be treated as the knowledge source. The prompt requires answers to use only retrieved context.

## Guardrails

The backend checks:

- whether the question is in scope
- whether the user is asking for personalized buy/surrender advice
- whether citations are present for in-scope answers

The system prompt adds policy-level rules against hallucination and personalized advice.
