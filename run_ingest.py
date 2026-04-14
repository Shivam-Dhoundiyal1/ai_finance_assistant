"""Ingest knowledge base into Chroma. Run from project root: python run_ingest.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.rag.ingest import ingest_documents

if __name__ == "__main__":
    n = ingest_documents()
    print(f"Ingested {n} chunks into the knowledge base.")
