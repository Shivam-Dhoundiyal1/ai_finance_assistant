"""Pytest configuration and shared fixtures."""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any


@pytest.fixture
def sample_portfolio() -> Dict[str, Any]:
    """Sample portfolio for testing."""
    return {
        "user_id": "test_user",
        "holdings": [
            {"symbol": "AAPL", "quantity": 10, "cost_basis": 150},
            {"symbol": "GOOGL", "quantity": 5, "cost_basis": 2800},
            {"symbol": "MSFT", "quantity": 8, "cost_basis": 380},
        ],
        "created_at": "2024-01-01",
        "last_updated": "2024-03-30",
    }


@pytest.fixture
def portfolio_file(sample_portfolio) -> Path:
    """Temporary portfolio JSON file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(sample_portfolio, f)
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def mock_market_data() -> Dict[str, Any]:
    """Mock market quote data."""
    return {
        "AAPL": {
            "symbol": "AAPL",
            "price": 175.50,
            "change": 2.50,
            "change_percent": 1.45,
            "currency": "USD",
            "source": "yfinance",
        },
        "GOOGL": {
            "symbol": "GOOGL",
            "price": 140.25,
            "change": -5.75,
            "change_percent": -3.94,
            "currency": "USD",
            "source": "yfinance",
        },
        "MSFT": {
            "symbol": "MSFT",
            "price": 420.00,
            "change": 15.00,
            "change_percent": 3.70,
            "currency": "USD",
            "source": "yfinance",
        },
    }


@pytest.fixture
def mock_rag_context() -> list:
    """Mock RAG retrieval context."""
    return [
        {
            "text": "Diversification is the practice of spreading investments across different assets...",
            "source": "03-diversification.md",
            "chunk_index": 0,
            "rank": 1,
        },
        {
            "text": "A well-diversified portfolio reduces unsystematic risk by holding many different securities...",
            "source": "03-diversification.md",
            "chunk_index": 1,
            "rank": 2,
        },
    ]


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = AsyncMock()
    mock_result = MagicMock()
    mock_result.content = "This is a mock LLM response about diversification."
    llm.ainvoke.return_value = mock_result
    return llm


@pytest.fixture
def mock_chat_response() -> Dict[str, Any]:
    """Mock chat API response."""
    return {
        "response": "Diversification is the practice of spreading investments...",
        "agent": "finance_qa",
        "sources": ["03-diversification.md"],
        "routing_confidence": 0.95,
        "success": True,
    }


@pytest.fixture
def mock_portfolio_response() -> Dict[str, Any]:
    """Mock portfolio API response."""
    return {
        "holdings": [
            {"symbol": "AAPL", "quantity": 10, "current_price": 175.50, "value": 1755.00},
            {"symbol": "GOOGL", "quantity": 5, "current_price": 140.25, "value": 701.25},
            {"symbol": "MSFT", "quantity": 8, "current_price": 420.00, "value": 3360.00},
        ],
        "total_value": 5816.25,
        "currency": "USD",
    }


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = MagicMock()
    settings.openai_api_key = "test-api-key"
    settings.gemini_api_key = None
    settings.alpha_vantage_api_key = "test-av-key"
    settings.llm_provider = "openai"
    settings.llm_model = "gpt-3.5-turbo"
    settings.debug = False
    return settings
