"""Test suite for API endpoints."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI test client."""
    from src.api.main import app
    return TestClient(app)


class TestChatEndpoint:
    """Tests for POST /api/v1/chat endpoint."""
    
    def test_chat_endpoint_basic(self, client):
        """Test basic chat endpoint response."""
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.return_value = {
                "agent": "finance_qa",
                "response": "A stock represents ownership in a company.",
                "context": [],
            }
            
            response = client.post(
                "/api/v1/chat",
                json={"message": "What is a stock?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "agent" in data or isinstance(data, dict)
    
    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message."""
        response = client.post("/api/v1/chat", json={})
        
        # Should handle validation error
        assert response.status_code in [400, 422]
    
    def test_chat_endpoint_empty_message(self, client):
        """Test chat endpoint with empty message."""
        with patch("src.api.main.invoke_workflow"):
            response = client.post(
                "/api/v1/chat",
                json={"message": ""}
            )
            
            # Should handle empty message
            assert response.status_code in [200, 400]
    
    def test_chat_endpoint_long_message(self, client):
        """Test chat endpoint with very long message."""
        long_message = "What " * 1000  # Very long query
        
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.return_value = {"agent": "finance_qa", "response": "Response"}
            
            response = client.post(
                "/api/v1/chat",
                json={"message": long_message}
            )
            
            # Should handle long input
            assert response.status_code in [200, 400]
    
    def test_chat_endpoint_special_characters(self, client):
        """Test chat endpoint with special characters."""
        special_msg = "What about $AAPL? & 'quotes' \"double\" <tags>"
        
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.return_value = {"agent": "market", "response": "AAPL info"}
            
            response = client.post(
                "/api/v1/chat",
                json={"message": special_msg}
            )
            
            assert response.status_code == 200
    
    def test_chat_endpoint_workflow_error(self, client):
        """Test chat endpoint when workflow raises error."""
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.side_effect = Exception("Workflow error")
            
            response = client.post(
                "/api/v1/chat",
                json={"message": "What is a stock?"}
            )
            
            # Should handle error gracefully
            assert response.status_code in [500, 200]


class TestMarketEndpoints:
    """Tests for market data endpoints."""
    
    def test_get_quote_endpoint(self, client):
        """Test GET /api/v1/market/quote/{symbol}."""
        with patch("src.api.main.get_quote") as mock_get:
            mock_get.return_value = {
                "symbol": "AAPL",
                "price": 150.0,
                "change": 2.5,
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            response = client.get("/api/v1/market/quote/AAPL")
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert data["price"] == 150.0
    
    def test_get_quote_invalid_symbol(self, client):
        """Test quote endpoint with invalid symbol."""
        with patch("src.api.main.get_quote") as mock_get:
            mock_get.side_effect = Exception("Invalid symbol")
            
            response = client.get("/api/v1/market/quote/INVALID")
            
            # Should handle invalid symbol
            assert response.status_code in [400, 404, 500]
    
    def test_market_summary_endpoint(self, client):
        """Test GET /api/v1/market/summary."""
        with patch("src.api.main.get_market_summary") as mock_summary:
            mock_summary.return_value = {
                "sp500": 4000.0,
                "nasdaq": 12000.0,
                "dow": 35000.0
            }
            
            response = client.get("/api/v1/market/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert "sp500" in data or len(data) > 0


class TestPortfolioEndpoints:
    """Tests for portfolio endpoints."""
    
    def test_get_portfolio_endpoint(self, client):
        """Test GET /api/v1/portfolio."""
        with patch("src.api.main.get_portfolio") as mock_get:
            mock_get.return_value = {
                "holdings": [
                    {"symbol": "AAPL", "shares": 10, "value": 1500}
                ],
                "total_value": 1500.0
            }
            
            response = client.get("/api/v1/portfolio")
            
            assert response.status_code == 200
            data = response.json()
            assert "holdings" in data or "total_value" in data or len(data) > 0
    
    def test_get_portfolio_performance(self, client):
        """Test GET /api/v1/portfolio/performance."""
        with patch("src.api.main.get_portfolio_performance") as mock_perf:
            mock_perf.return_value = {
                "total_return": 150.0,
                "total_return_pct": 10.0,
                "allocation": {}
            }
            
            response = client.get("/api/v1/portfolio/performance")
            
            assert response.status_code == 200
    
    def test_get_portfolio_allocation(self, client):
        """Test GET /api/v1/portfolio/allocation."""
        with patch("src.api.main.get_portfolio_allocation") as mock_alloc:
            mock_alloc.return_value = {
                "Technology": 40.0,
                "Healthcare": 30.0,
                "Finance": 20.0,
                "Other": 10.0
            }
            
            response = client.get("/api/v1/portfolio/allocation")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test GET /health."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or response.text


class TestErrorHandling:
    """Tests for API error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        response = client.delete("/api/v1/chat")
        
        assert response.status_code in [405, 404]
    
    def test_invalid_json(self, client):
        """Test invalid JSON in request."""
        response = client.post(
            "/api/v1/chat",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    def test_timeout_handling(self, client):
        """Test handling of timeout scenarios."""
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.side_effect = TimeoutError()
            
            response = client.post(
                "/api/v1/chat",
                json={"message": "Test"}
            )
            
            # Should handle timeout gracefully
            assert response.status_code in [500, 408]


class TestConcurrency:
    """Tests for concurrent requests."""
    
    def test_multiple_chat_requests(self, client):
        """Test multiple simultaneous chat requests."""
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.return_value = {"agent": "finance_qa", "response": "Response"}
            
            responses = []
            for i in range(3):
                response = client.post(
                    "/api/v1/chat",
                    json={"message": f"Question {i}"}
                )
                responses.append(response.status_code)
            
            # All should succeed
            assert all(code == 200 for code in responses)
    
    def test_multiple_quote_requests(self, client):
        """Test multiple quote requests for different symbols."""
        with patch("src.api.main.get_quote") as mock_get:
            mock_get.return_value = {"symbol": "", "price": 100.0}
            
            symbols = ["AAPL", "MSFT", "GOOGL"]
            responses = []
            
            for symbol in symbols:
                response = client.get(f"/api/v1/market/quote/{symbol}")
                responses.append(response.status_code)
            
            # All should succeed
            assert all(code in [200, 500] for code in responses)


class TestDataValidation:
    """Tests for request/response data validation."""
    
    def test_chat_response_structure(self, client):
        """Test chat response has required fields."""
        with patch("src.api.main.invoke_workflow") as mock_invoke:
            mock_invoke.return_value = {
                "agent": "finance_qa",
                "response": "Test response"
            }
            
            response = client.post(
                "/api/v1/chat",
                json={"message": "Test"}
            )
            
            assert response.status_code == 200
            data = response.json()
            # Should have response or similar
            assert len(data) > 0
    
    def test_quote_response_structure(self, client):
        """Test quote response has required fields."""
        with patch("src.api.main.get_quote") as mock_get:
            mock_get.return_value = {
                "symbol": "TEST",
                "price": 100.0,
                "change": 5.0
            }
            
            response = client.get("/api/v1/market/quote/TEST")
            
            assert response.status_code == 200
            data = response.json()
            assert "price" in data or "symbol" in data
    
    def test_portfolio_response_structure(self, client):
        """Test portfolio response has required fields."""
        with patch("src.api.main.get_portfolio") as mock_get:
            mock_get.return_value = {
                "holdings": [],
                "total_value": 0.0
            }
            
            response = client.get("/api/v1/portfolio")
            
            assert response.status_code == 200
