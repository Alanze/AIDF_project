import re

from app.rag.knowledge_base import KnowledgeBase
from app.schemas.knowledge import KnowledgeChunk


TOKEN_RE = re.compile(r"[a-zA-Z0-9%]+|[\u4e00-\u9fff]")
CHINESE_SEQUENCE_RE = re.compile(r"[\u4e00-\u9fff]+")
DOMAIN_TERMS = [
    "现金价值",
    "現金價值",
    "每月费用",
    "每月費用",
    "宽限期",
    "寬限期",
    "保单终止",
    "保單終止",
    "保单失效",
    "保單失效",
    "暂停缴费",
    "暫停繳費",
    "暂停缴付保费",
    "暫停繳付保費",
    "提取现金",
    "提取現金",
    "提款",
    "退保",
    "身故保障",
    "额外回报",
    "額外回報",
    "保证",
    "保證",
    "派息率",
    "利息",
    "费用",
    "費用",
    "不足",
    "终止",
    "終止",
    "失效",
]


def tokenize(text: str) -> set[str]:
    tokens = {token.lower() for token in TOKEN_RE.findall(text)}
    lowered = text.lower()

    for term in DOMAIN_TERMS:
        if term in text:
            tokens.add(term.lower())

    for sequence in CHINESE_SEQUENCE_RE.findall(text):
        for size in (2, 3, 4):
            for index in range(0, max(len(sequence) - size + 1, 0)):
                tokens.add(sequence[index : index + size])

    if "cash value" in lowered:
        tokens.add("cash value")
    if "premium payment" in lowered or "premium payments" in lowered:
        tokens.add("premium payment")
    return tokens


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
        if not scored:
            return []

        best_score = scored[0][0]
        minimum_score = max(2, best_score * 0.45)
        filtered = [(score, chunk) for score, chunk in scored if score >= minimum_score]
        return [chunk for _, chunk in filtered[:top_k]]
