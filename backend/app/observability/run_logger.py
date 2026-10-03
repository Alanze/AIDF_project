import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.guardrails.safety import QuestionAssessment
from app.schemas.chat import ChatResponse
from app.schemas.knowledge import KnowledgeChunk


def log_chat_run(
    *,
    question: str,
    assessment: QuestionAssessment,
    chunks: list[KnowledgeChunk],
    response: ChatResponse,
) -> None:
    if not settings.run_log_enabled:
        return

    try:
        created_at = datetime.now(UTC)
        request_id = f"{created_at.strftime('%H%M%S')}_{uuid4().hex[:8]}"
        run_dir = Path(settings.run_log_dir) / created_at.strftime("%Y-%m-%d") / request_id
        run_dir.mkdir(parents=True, exist_ok=True)

        _write_json(
            run_dir / "meta.json",
            {
                "request_id": request_id,
                "created_at_utc": created_at.isoformat(),
                "model_provider": settings.model_provider,
                "model_name": settings.model_name,
                "llm_base_url": settings.effective_llm_base_url,
                "llm_api_key_configured": bool(settings.effective_llm_api_key),
                "knowledge_base_path": settings.knowledge_base_path,
                "top_k": settings.top_k,
                "language": response.language,
                "scope_status": response.scope_status,
                "confidence": response.confidence,
                "retrieved_chunk_count": len(chunks),
                "citation_count": len(response.citations),
                "has_case_context": response.case_context is not None,
            },
        )
        _write_json(
            run_dir / "request.json",
            {
                "question": question,
                "assessment": {
                    "language": assessment.language,
                    "scope_status": assessment.scope_status,
                    "personal_advice_warning": assessment.personal_advice_warning,
                },
            },
        )
        _write_json(
            run_dir / "retrieval.json",
            {
                "chunks": [
                    {
                        "id": chunk.id,
                        "page": chunk.page,
                        "category": chunk.category,
                        "section_title": chunk.section_title,
                        "summary_en": chunk.summary_en,
                        "summary_zh": chunk.summary_zh,
                        "important_caveats": chunk.important_caveats,
                        "important_caveats_zh": chunk.important_caveats_zh,
                    }
                    for chunk in chunks
                ]
            },
        )
        _write_json(
            run_dir / "response.json",
            response.model_dump(mode="json"),
        )
    except OSError:
        return


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
