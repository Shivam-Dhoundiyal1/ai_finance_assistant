"""Vector store and collection configuration for RAG."""
from pathlib import Path

from src.core.config import get_settings


class KnowledgeBase:
    """Chroma-backed knowledge base settings."""

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
        embedding_model: str | None = None,
    ) -> None:
        s = get_settings()
        self.persist_dir = persist_dir or s.rag_persist_directory
        self.collection_name = collection_name or s.rag_collection_name
        self.embedding_model = embedding_model or s.rag_embedding_model

    def resolve_persist_path(self, project_root: Path | None = None) -> Path:
        root = project_root or Path(__file__).resolve().parents[2]
        path = root / self.persist_dir
        path.mkdir(parents=True, exist_ok=True)
        return path
