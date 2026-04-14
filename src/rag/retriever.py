"""Retrieve relevant context from the knowledge base for RAG."""
from pathlib import Path
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.core.config import get_settings
from src.rag.knowledge_base import KnowledgeBase


def _build_retriever(top_k: int):
    kb = KnowledgeBase()
    root = Path(__file__).resolve().parents[2]
    persist_path = kb.resolve_persist_path(root)
    embeddings = HuggingFaceEmbeddings(model_name=kb.embedding_model)
    vector_store = Chroma(
        collection_name=kb.collection_name,
        persist_directory=str(persist_path),
        embedding_function=embeddings,
    )
    return vector_store.as_retriever(search_kwargs={"k": top_k})


def retrieve_context(query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    """
    Retrieve top-k relevant chunks for the query.
    Returns list of dicts with keys: text, source, chunk_index, rank.
    """
    s = get_settings()
    k = top_k if top_k is not None else s.rag_top_k
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
