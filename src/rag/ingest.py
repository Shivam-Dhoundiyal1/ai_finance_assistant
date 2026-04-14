"""Ingest markdown documents into the vector store."""
from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import get_settings
from src.rag.knowledge_base import KnowledgeBase


def read_markdown_files(data_dir: str | Path | None = None) -> List[Tuple[str, str]]:
    """Read all .md files from data_dir. Returns list of (file_path, content)."""
    s = get_settings()
    root = Path(data_dir or s.rag_knowledge_path)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[2] / root
    if not root.exists():
        return []
    documents: List[Tuple[str, str]] = []
    for file_path in root.rglob("*.md"):
        try:
            content = file_path.read_text(encoding="utf-8")
            documents.append((str(file_path), content))
        except Exception:
            continue
    return documents


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> List[str]:
    """Split text into overlapping chunks."""
    if not text.strip():
        return []
    s = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or s.rag_chunk_size,
        chunk_overlap=overlap or s.rag_chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def ingest_documents(data_dir: str | Path | None = None) -> int:
    """Ingest markdown files into Chroma. Returns number of chunks indexed."""
    from langchain_chroma import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings

    kb = KnowledgeBase()
    root = Path(__file__).resolve().parents[2]
    persist_path = kb.resolve_persist_path(root)
    embeddings = HuggingFaceEmbeddings(model_name=kb.embedding_model)
    vector_store = Chroma(
        collection_name=kb.collection_name,
        persist_directory=str(persist_path),
        embedding_function=embeddings,
    )

    docs = read_markdown_files(data_dir=data_dir)
    if not docs:
        return 0

    all_docs: List[Document] = []
    for source, content in docs:
        chunks = chunk_text(content)
        for index, chunk in enumerate(chunks):
            all_docs.append(
                Document(
                    page_content=chunk,
                    metadata={"source": source, "chunk_index": index},
                )
            )

    vector_store.add_documents(all_docs)
    return len(all_docs)
