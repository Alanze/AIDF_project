from fastapi import APIRouter

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

    if assessment.scope_status == "out_of_scope":
        return ChatResponse(
            answer=assessment.message,
            language=assessment.language,
            confidence="high",
            scope_status="out_of_scope",
            citations=[],
            caveats=["This answer is limited to the supplied FLEXI-ULife Prime Saver document."],
            suggested_followups=[
                "Ask about premium flexibility",
                "Ask about death benefit options",
                "Ask about exclusions or risks",
            ],
        )

    chunks = retriever.search(request.question, top_k=settings.top_k)
    if not chunks:
        return ChatResponse(
            answer=assessment.not_enough_context_message,
            language=assessment.language,
            confidence="low",
            scope_status="insufficient_context",
            citations=[],
            caveats=["No relevant evidence was retrieved from the supplied document."],
            suggested_followups=[],
        )

    return await generator.generate(
        question=request.question,
        chunks=chunks,
        language=assessment.language,
        advice_warning=assessment.personal_advice_warning,
    )
