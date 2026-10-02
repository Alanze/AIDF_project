import json

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.guardrails.validators import ensure_citation_consistency, ensure_grounded_response
from app.case_understanding.schemas import UserCase
from app.schemas.chat import ChatResponse, Citation
from app.schemas.knowledge import KnowledgeChunk


class AnswerGenerator:
    async def generate(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        language: str,
        advice_warning: str | None,
        user_case: UserCase | None = None,
    ) -> ChatResponse:
        if settings.model_provider in {"openai_compatible", "qwen"}:
            try:
                response = await self._generate_with_openai_compatible(question, chunks, language, advice_warning, user_case)
            except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, KeyError, ValidationError):
                response = self._provider_error_response(chunks, language, user_case)
        else:
            response = self._generate_mock(question, chunks, language, advice_warning, user_case)
        response.case_context = user_case
        response = ensure_citation_consistency(response, chunks)
        return ensure_grounded_response(response)

    def _provider_error_response(
        self,
        chunks: list[KnowledgeChunk],
        language: str,
        user_case: UserCase | None,
    ) -> ChatResponse:
        evidence_chunks = chunks[:3]
        citations = [
            Citation(
                source="FLEXI-ULife Prime Saver.pdf",
                page=chunk.page,
                section=chunk.section_title,
                chunk_id=chunk.id,
            )
            for chunk in evidence_chunks
        ]

        if language.startswith("zh"):
            answer = "模型服务暂时不可用，当前无法生成完整回答。系统已经完成资料检索，你可以稍后重试；如果问题涉及个人保单决策，请参考正式保单文件或咨询合资格保险顾问。"
            caveats = ["Qwen/DashScope API 暂时无法连接或返回格式异常，因此没有使用模型生成最终答案。"]
            followups = ["稍后重试同一问题", "先询问暂停缴费的条款风险", "检查 /health 中的模型配置"]
        else:
            answer = "The model service is temporarily unavailable, so a complete generated answer could not be produced. The system retrieved relevant document sources; please retry later or consult the formal policy document or a qualified insurance professional for case-specific decisions."
            caveats = ["The Qwen/DashScope API could not be reached or returned an invalid response, so the final model answer was not generated."]
            followups = ["Retry the same question later", "Ask about premium flexibility risks", "Check model configuration in /health"]

        return ChatResponse(
            answer=answer,
            language=language,
            confidence="low",
            scope_status="insufficient_context",
            case_context=user_case,
            citations=citations,
            caveats=caveats,
            suggested_followups=followups,
        )

    def _generate_mock(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        language: str,
        advice_warning: str | None,
        user_case: UserCase | None,
    ) -> ChatResponse:
        evidence_chunks = self._select_evidence_chunks(chunks)
        first = evidence_chunks[0]
        if language.startswith("zh"):
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

        caveat_items = self._localized_caveats(first, language)
        caveats = [f"{caveat_prefix} {item}" for item in caveat_items]
        citations = [
            Citation(
                source="FLEXI-ULife Prime Saver.pdf",
                page=chunk.page,
                section=chunk.section_title,
                chunk_id=chunk.id,
            )
            for chunk in evidence_chunks
        ]
        return ChatResponse(
            answer=answer,
            language=language,
            confidence="medium",
            scope_status="in_scope",
            case_context=user_case,
            citations=citations,
            caveats=caveats,
            suggested_followups=followups,
        )

    def _select_evidence_chunks(self, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        return chunks[:1]

    def _localized_caveats(self, chunk: KnowledgeChunk, language: str) -> list[str]:
        if language.startswith("zh"):
            return chunk.important_caveats_zh
        return chunk.important_caveats

    async def _generate_with_openai_compatible(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        language: str,
        advice_warning: str | None,
        user_case: UserCase | None,
    ) -> ChatResponse:
        system_prompt = self._load_system_prompt()
        context = self._format_context(chunks)
        user_prompt = {
            "question": question,
            "language": language,
            "advice_warning": advice_warning,
            "user_case": user_case.model_dump(exclude_none=True) if user_case else None,
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
        with open("backend/app/prompts/system_prompt.md", "r", encoding="utf-8") as file:
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
                "important_caveats_zh": chunk.important_caveats_zh,
            }
            for chunk in chunks
        ]
