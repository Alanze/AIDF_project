import json

import httpx

from app.core.config import settings
from app.guardrails.validators import ensure_grounded_response
from app.schemas.chat import ChatResponse, Citation
from app.schemas.knowledge import KnowledgeChunk


class AnswerGenerator:
    async def generate(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        language: str,
        advice_warning: str | None,
    ) -> ChatResponse:
        if settings.model_provider in {"openai_compatible", "qwen"}:
            response = await self._generate_with_openai_compatible(question, chunks, language, advice_warning)
        else:
            response = self._generate_mock(question, chunks, language, advice_warning)
        return ensure_grounded_response(response)

    def _generate_mock(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        language: str,
        advice_warning: str | None,
    ) -> ChatResponse:
        first = chunks[0]
        if language == "zh":
            answer = first.summary_zh
            if advice_warning:
                answer = f"{advice_warning}\n\n{answer}"
            caveat_prefix = "需要注意："
            followups = ["这个功能有什么限制？", "相关费用是什么？", "资料中提到哪些风险？"]
        else:
            answer = first.summary_en
            if advice_warning:
                answer = f"{advice_warning}\n\n{answer}"
            caveat_prefix = "Important:"
            followups = ["What are the limitations?", "What fees apply?", "What risks does the document mention?"]

        caveats = [f"{caveat_prefix} {item}" for item in first.important_caveats]
        citations = [
            Citation(
                source="FLEXI-ULife Prime Saver.pdf",
                page=chunk.page,
                section=chunk.section_title,
                chunk_id=chunk.id,
            )
            for chunk in chunks
        ]
        return ChatResponse(
            answer=answer,
            language=language,
            confidence="medium",
            scope_status="in_scope",
            citations=citations,
            caveats=caveats,
            suggested_followups=followups,
        )

    async def _generate_with_openai_compatible(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        language: str,
        advice_warning: str | None,
    ) -> ChatResponse:
        system_prompt = self._load_system_prompt()
        context = self._format_context(chunks)
        user_prompt = {
            "question": question,
            "language": language,
            "advice_warning": advice_warning,
            "retrieved_context": context,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            result = await client.post(
                f"{settings.effective_llm_base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.effective_llm_api_key}"},
                json={
                    "model": settings.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                },
            )
            result.raise_for_status()

        content = result.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return ChatResponse.model_validate(parsed)

    def _load_system_prompt(self) -> str:
        with open("backend/app/prompts/system_prompt.txt", "r", encoding="utf-8") as file:
            return file.read()

    def _format_context(self, chunks: list[KnowledgeChunk]) -> list[dict[str, object]]:
        return [
            {
                "id": chunk.id,
                "page": chunk.page,
                "section": chunk.section_title,
                "category": chunk.category,
                "summary_en": chunk.summary_en,
                "summary_zh": chunk.summary_zh,
                "source_text": chunk.source_text,
                "important_caveats": chunk.important_caveats,
            }
            for chunk in chunks
        ]
