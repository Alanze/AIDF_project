from fastapi import APIRouter

from app.case_understanding.extractor import extract_user_case
from app.core.config import settings
from app.guardrails.safety import assess_question
from app.rag.generator import AnswerGenerator
from app.rag.knowledge_base import KnowledgeBase
from app.rag.retriever import Retriever
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

knowledge_base = KnowledgeBase(settings.knowledge_base_path)
retriever = Retriever(knowledge_base)
generator = AnswerGenerator()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    assessment = assess_question(request.question)
    user_case = extract_user_case(request.question)
    case_context = user_case if user_case.has_case_context else None

    if assessment.scope_status == "out_of_scope":
        caveat = (
            "本回答仅限于已提供的 FLEXI-ULife Prime Saver 产品资料。"
            if assessment.language.startswith("zh")
            else "This answer is limited to the supplied FLEXI-ULife Prime Saver document."
        )
        followups = (
            ["询问缴费弹性", "询问身故保障选择", "询问除外责任或风险"]
            if assessment.language.startswith("zh")
            else [
                "Ask about premium flexibility",
                "Ask about death benefit options",
                "Ask about exclusions or risks",
            ]
        )
        return ChatResponse(
            answer=assessment.message,
            language=assessment.language,
            confidence="high",
            scope_status="out_of_scope",
            case_context=case_context,
            citations=[],
            caveats=[caveat],
            suggested_followups=followups,
        )

    chunks = retriever.search(request.question, top_k=settings.top_k)
    chunks = retriever.expand_for_case(chunks, case_context)
    if not chunks:
        return ChatResponse(
            answer=assessment.not_enough_context_message,
            language=assessment.language,
            confidence="low",
            scope_status="insufficient_context",
            case_context=case_context,
            citations=[],
            caveats=["No relevant evidence was retrieved from the supplied document."],
            suggested_followups=[],
        )

    return await generator.generate(
        question=request.question,
        chunks=chunks,
        language=assessment.language,
        advice_warning=assessment.personal_advice_warning,
        user_case=case_context,
    )
