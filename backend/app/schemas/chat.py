from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class Citation(BaseModel):
    source: str
    page: int
    section: str
    chunk_id: str


class ChatResponse(BaseModel):
    answer: str
    language: str
    confidence: str
    scope_status: str
    citations: list[Citation]
    caveats: list[str]
    suggested_followups: list[str]
