import re

from app.rag.knowledge_base import KnowledgeBase
from app.schemas.knowledge import KnowledgeChunk


TOKEN_RE = re.compile(r"[a-zA-Z0-9%]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


class Retriever:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base

    def search(self, question: str, top_k: int = 5) -> list[KnowledgeChunk]:
        query_tokens = tokenize(question)
        scored: list[tuple[float, KnowledgeChunk]] = []

        for chunk in self.knowledge_base.chunks:
            haystack = " ".join(
                [
                    chunk.category,
                    chunk.section_title,
                    chunk.summary_en,
                    chunk.summary_zh,
                    chunk.source_text,
                    " ".join(chunk.keywords),
                ]
            )
            haystack_tokens = tokenize(haystack)
            overlap = query_tokens & haystack_tokens
            keyword_hits = sum(1 for keyword in chunk.keywords if keyword.lower() in question.lower() or keyword in question)
            score = len(overlap) + keyword_hits * 2
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
