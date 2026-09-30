from pydantic import BaseModel


class KnowledgeChunk(BaseModel):
    id: str
    product: str
    category: str
    section_title: str
    page: int
    languages: list[str]
    summary_en: str
    summary_zh: str
    source_text: str
    important_caveats: list[str] = []
    important_caveats_zh: list[str] = []
    keywords: list[str] = []
