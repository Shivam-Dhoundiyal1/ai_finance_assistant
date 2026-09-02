"""Retrieve relevant context from the knowledge base for RAG."""
import gc
from pathlib import Path
from typing import Any, Dict, List

from src.core.config import get_settings
from src.rag.knowledge_base import KnowledgeBase


# Global cache for embeddings model to avoid repeated loading
_embedding_model = None
_vector_store = None


def _get_embeddings():
    """Lazy-load and cache embeddings model."""
    global _embedding_model
    if _embedding_model is None:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        kb = KnowledgeBase()
        _embedding_model = HuggingFaceEmbeddings(model_name=kb.embedding_model)
    return _embedding_model


def _get_vector_store():
    """Lazy-load and cache the Chroma vector store."""
    global _vector_store
    if _vector_store is None:
        from langchain_chroma import Chroma

        kb = KnowledgeBase()
        root = Path(__file__).resolve().parents[2]
        persist_path = kb.resolve_persist_path(root)
        embeddings = _get_embeddings()
        _vector_store = Chroma(
            collection_name=kb.collection_name,
            persist_directory=str(persist_path),
            embedding_function=embeddings,
        )
    return _vector_store


def _build_retriever(top_k: int):
    """Build retriever with cached components."""
    vector_store = _get_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": top_k})


def retrieve_context(query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    """
    Retrieve top-k relevant chunks for the query.
    Returns list of dicts with keys: text, source, chunk_index, rank.
    """
    s = get_settings()
    k = top_k if top_k is not None else s.rag_top_k
    retriever = None
    documents = []

    try:
        retriever = _build_retriever(top_k=k)
        documents = retriever.invoke(query)

        context_items: List[Dict[str, Any]] = []
        for rank, doc in enumerate(documents, start=1):
            metadata = doc.metadata or {}
            context_items.append({
                "text": doc.page_content,
                "source": metadata.get("source"),
                "chunk_index": metadata.get("chunk_index"),
                "rank": rank,
            })
        return context_items
    finally:
        del retriever
        del documents
        gc.collect()
