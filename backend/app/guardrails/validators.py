import re

from app.schemas.chat import ChatResponse, Citation
from app.schemas.knowledge import KnowledgeChunk


PAGE_REF_RE = re.compile(r"(?:p\.|page\s*|第)\s*(\d{1,2})\s*(?:页|頁)?", re.IGNORECASE)


def ensure_grounded_response(response: ChatResponse) -> ChatResponse:
    if response.scope_status == "in_scope" and not response.citations:
        response.scope_status = "insufficient_context"
        response.confidence = "low"
        response.caveats.append("The answer was downgraded because no citation was available.")
    return response


def ensure_citation_consistency(response: ChatResponse, retrieved_chunks: list[KnowledgeChunk]) -> ChatResponse:
    referenced_pages = _referenced_pages(response)
    if not referenced_pages:
        return response

    cited_pages = {citation.page for citation in response.citations}
    chunks_by_page = _chunks_by_page(retrieved_chunks)

    for page in sorted(referenced_pages - cited_pages):
        chunk = chunks_by_page.get(page)
        if chunk:
            response.citations.append(
                Citation(
                    source="FLEXI-ULife Prime Saver.pdf",
                    page=chunk.page,
                    section=chunk.section_title,
                    chunk_id=chunk.id,
                )
            )

    return response


def _referenced_pages(response: ChatResponse) -> set[int]:
    text = " ".join([response.answer, *response.caveats])
    return {int(match.group(1)) for match in PAGE_REF_RE.finditer(text)}


def _chunks_by_page(chunks: list[KnowledgeChunk]) -> dict[int, KnowledgeChunk]:
    by_page: dict[int, KnowledgeChunk] = {}
    for chunk in chunks:
        by_page.setdefault(chunk.page, chunk)
    return by_page
