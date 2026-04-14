"""Tests for RAG retriever (requires ingested knowledge base)."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.retriever import retrieve_context


def test_retrieve_context_returns_list():
    # May be empty if no docs ingested
    result = retrieve_context("what is investing", top_k=2)
    assert isinstance(result, list)
    for item in result:
        assert "text" in item
        assert "source" in item or "rank" in item


class TestRAGRetriever:
    """Tests for RAG document retrieval."""
    
    def test_retrieve_context_structure(self):
        """Test that retrieve_context returns properly structured data."""
        # This tests that if retrievals work, they have the right structure
        results = retrieve_context("test query", top_k=1)
        
        # Even if empty, should be a list
        assert isinstance(results, list)
        
        # If not empty, should have expected structure
        for item in results:
            assert "text" in item
            # source is optional
            if "source" in item:
                assert isinstance(item["source"], str)


class TestChromaIntegration:
    """Tests for Chroma vector database integration."""
    
    def test_knowledge_base_initialization(self):
        """Test KnowledgeBase class initializes properly."""
        from src.rag.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        
        # Should have expected attributes
        assert hasattr(kb, "persist_dir")
        assert hasattr(kb, "collection_name")
        assert hasattr(kb, "embedding_model")
    
    def test_knowledge_base_resolve_path(self):
        """Test path resolution for knowledge base."""
        from src.rag.knowledge_base import KnowledgeBase
        from pathlib import Path
        
        kb = KnowledgeBase()
        root = Path(__file__).resolve().parents[2]
        
        path = kb.resolve_persist_path(root)
        
        assert isinstance(path, Path)
        assert path.parent == root


class TestRAGQualityMetrics:
    """Tests for RAG quality/relevance."""
    
    def test_different_query_types(self):
        """Test retrieval works with different query types."""
        queries = [
            "Stock definition",
            "Bond investing",
            "Portfolio diversification",
            "Tax planning",
        ]
        
        for query in queries:
            results = retrieve_context(query, top_k=2)
            # Should return list without error
            assert isinstance(results, list)


class TestRAGErrorHandling:
    """Tests for RAG error handling and edge cases."""
    
    def test_retrieve_empty_query(self):
        """Test retrieval with empty query."""
        results = retrieve_context("", top_k=5)
        
        # Should handle gracefully
        assert isinstance(results, list)
    
    def test_retrieve_very_short_query(self):
        """Test retrieval with very short query."""
        results = retrieve_context("a", top_k=5)
        
        # Should return list
        assert isinstance(results, list)
    
    def test_retrieve_very_long_query(self):
        """Test retrieval with very long query."""
        long_query = " ".join(["word"] * 1000)
        
        results = retrieve_context(long_query, top_k=5)
        
        # Should handle long queries
        assert isinstance(results, list)
    
    def test_retrieve_special_characters(self):
        """Test retrieval with special characters."""
        queries = [
            "What is a $AAPL stock?",
            "Bonds & derivatives",
            "Portfolio <rebalance>?",
        ]
        
        for query in queries:
            results = retrieve_context(query, top_k=3)
            assert isinstance(results, list)
