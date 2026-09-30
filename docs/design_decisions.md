# Design Decisions

## Use OpenAI-Compatible Model APIs

The project can run against local open-source model servers such as Ollama, vLLM, and LM Studio. This avoids locking the demo to one paid provider.

## Keep A Mock Provider

`MODEL_PROVIDER=mock` gives deterministic extractive answers from retrieved chunks. This is useful for development, Docker validation, and situations where the reviewer does not have a local model ready.

## Store Knowledge As JSON

JSON chunks are easy to inspect, test, and improve. They also make it clear how PDF evidence is categorized.

## Cite Page-Level Sources

The supplied PDF is a product brochure. Page-level citation is practical and enough for this demo. A production system could add bounding boxes or paragraph-level source spans.

## Prefer Conservative Insurance Answers

Insurance answers should mention caveats, non-guaranteed assumptions, fees, exclusions, and lapse risk. The system should avoid personalized recommendations.
