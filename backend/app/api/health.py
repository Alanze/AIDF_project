from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "model_provider": settings.model_provider,
        "model_name": settings.model_name,
        "llm_base_url": settings.effective_llm_base_url,
        "llm_api_key_configured": bool(settings.effective_llm_api_key),
        "knowledge_base_path": settings.knowledge_base_path,
        "top_k": settings.top_k,
    }
