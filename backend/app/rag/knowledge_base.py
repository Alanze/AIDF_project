import json
from pathlib import Path

from app.schemas.knowledge import KnowledgeChunk


class KnowledgeBase:
    def __init__(self, path: str):
        self.path = Path(path)
        self._chunks: list[KnowledgeChunk] | None = None

    @property
    def chunks(self) -> list[KnowledgeChunk]:
        if self._chunks is None:
            with self.path.open("r", encoding="utf-8") as file:
                raw_chunks = json.load(file)
            self._chunks = [KnowledgeChunk.model_validate(item) for item in raw_chunks]
        return self._chunks
