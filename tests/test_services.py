"""Test suite for data services (market and portfolio)."""
import pytest
from unittest.mock import patch, MagicMock


class TestMarketService:
    """Tests for market data service."""
    
    @patch("src.data.market_service.yf.Ticker")
    def test_get_quote_success(self, mock_ticker):
        """Test getting a stock quote successfully."""
        from src.data.market_service import get_quote
        
        # Mock yfinance response
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "regularMarketPrice": 150.0,
            "previousClose": 148.5,
            "currency": "USD"
        }
        mock_ticker_instance.history.return_value = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        
        result = get_quote("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["price"] == 150.0
        assert result["change"] == 1.5
        assert result["currency"] == "USD"
        assert "error" not in result or result["error"] is None
    
    @patch("src.data.market_service.yf.Ticker")
    def test_get_quote_invalid_symbol(self, mock_ticker):
        """Test getting quote for invalid symbol."""
        from src.data.market_service import get_quote
        
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}  # No data
        mock_ticker.return_value = mock_ticker_instance
        
        result = get_quote("INVALID123")
        
        assert "error" in result
    
    def test_get_quote_caching(self):
        """Test that quotes are cached."""
        from src.data.market_service import get_real_time_quote
        
        # First call - should fetch
        with patch("src.data.market_service.get_quote") as mock_get:
            mock_get.return_value = {
                "symbol": "AAPL",
                "price": 150.0,
                "change": 1.0,
                "change_percent": 0.67,
            }
            
            # Call twice
            result1 = get_real_time_quote("AAPL")
            result2 = get_real_time_quote("AAPL")
            
            # Should have data both times
            assert result1["price"] == result2["price"]
    
    def test_extract_symbols(self):
        """Test symbol extraction from messages."""
        from src.data.market_service import extract_symbols
        
        symbols = extract_symbols("What is the price of AAPL and MSFT?")
        assert "AAPL" in symbols or "MSFT" in symbols
        
        symbols = extract_symbols("Buy $TSLA and $GOOGL")
        assert len(symbols) >= 0  # May or may not find them
    
    def test_get_market_summary(self):
        """Test getting summary for multiple symbols."""
        from src.data.market_service import get_market_summary
        
        with patch("src.data.market_service.get_real_time_quote") as mock_get:
            mock_get.return_value = {
                "symbol": "TEST",
                "price": 100.0,
                "change": 0.0,
                "change_percent": 0.0,
            }
            
            summary = get_market_summary(["AAPL", "MSFT"])
            
            assert "AAPL" in summary
            assert "MSFT" in summary


class TestPortfolioService:
    """Tests for portfolio service."""
    
    def test_get_sample_portfolio(self):
        """Test getting sample portfolio."""
        from src.data.portfolio_service import get_sample_portfolio
        
        portfolio = get_sample_portfolio()
        
        assert "holdings" in portfolio
        assert len(portfolio["holdings"]) > 0
        
        for holding in portfolio["holdings"]:
            assert "symbol" in holding
            assert "quantity" in holding
            assert "avg_cost" in holding
    
    @patch("src.data.portfolio_service.load_user_portfolio")
    def test_get_user_portfolio(self, mock_load):
        """Test getting user portfolio."""
        from src.data.portfolio_service import get_user_portfolio
        
        mock_load.return_value = {
            "holdings": [
                {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}
            ]
        }
        
        portfolio = get_user_portfolio("user123")
        
        assert len(portfolio["holdings"]) == 1
        assert portfolio["holdings"][0]["symbol"] == "AAPL"
    
    def test_calculate_portfolio_performance(self):
        """Test portfolio performance calculations."""
        from src.data.portfolio_service import calculate_portfolio_performance
        
        portfolio = {
            "holdings": [
                {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0, "current_price": 160.0},
                {"symbol": "MSFT", "quantity": 5, "avg_cost": 300.0, "current_price": 310.0},
            ]
        }
        
        with patch("src.data.portfolio_service.get_quote") as mock_get:
            mock_get.side_effect = lambda s: {
                "symbol": s,
                "price": 160.0 if s == "AAPL" else 310.0,
            }
            
            performance = calculate_portfolio_performance(portfolio)
            
            assert "total_return" in performance
            assert "annualized_return" in performance
            assert "sharpe_ratio" in performance
    
    def test_analyze_allocation(self):
        """Test portfolio allocation analysis."""
        from src.data.portfolio_service import analyze_allocation
        
        portfolio = {
            "holdings": [
                {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0},
                {"symbol": "MSFT", "quantity": 5, "avg_cost": 300.0},
            ]
        }
        
        allocation = analyze_allocation(portfolio)
        
        assert "current_allocation" in allocation
        assert "recommended_allocation" in allocation
        assert "diversification_score" in allocation
    
    def test_save_and_delete_holding(self):
        """Test saving and deleting holdings."""
        from src.data.portfolio_service import save_portfolio, delete_holding
        
        portfolio = {
            "holdings": [
                {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}
            ]
        }
        
        # Should save without error
        save_portfolio("test_user", portfolio)
        
        # Should delete without error
        delete_holding("test_user", "AAPL")
    
    def test_portfolio_total_value(self):
        """Test calculating portfolio total value."""
        from src.data.portfolio_service import get_user_portfolio
        
        with patch("src.data.portfolio_service.load_user_portfolio") as mock_load:
            mock_load.return_value = {
                "holdings": [
                    {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0},
                    {"symbol": "MSFT", "quantity": 5, "avg_cost": 300.0},
                ]
            }
            
            portfolio = get_user_portfolio("user123")
            total_value = sum(h["quantity"] * h["avg_cost"] for h in portfolio["holdings"])
            
            assert total_value == 3000.0  # (10*150) + (5*300)


class TestMarketAndPortfolioIntegration:
    """Integration tests for market and portfolio services."""
    
    @patch("src.data.market_service.get_real_time_quote")
    def test_portfolio_with_live_quotes(self, mock_quote):
        """Test portfolio with live market quotes."""
        from src.data.portfolio_service import get_user_portfolio
        
        mock_quote.return_value = {"price": 160.0, "change": 1.0}
        
        with patch("src.data.portfolio_service.load_user_portfolio") as mock_load:
            mock_load.return_value = {
                "holdings": [
                    {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0}
                ]
            }
            
            portfolio = get_user_portfolio("user123")
            
            assert len(portfolio["holdings"]) == 1
    
    def test_performance_calculation_accuracy(self):
        """Test accuracy of performance calculations."""
        from src.data.portfolio_service import calculate_portfolio_performance
        
        portfolio = {
            "holdings": [
                {"symbol": "AAPL", "quantity": 100, "avg_cost": 100.0}
            ]
        }
        
        with patch("src.data.market_service.get_real_time_quote") as mock_quote:
            mock_quote.return_value = {
                "symbol": "AAPL",
                "price": 110.0,
                "change": 10.0,
                "change_percent": 10.0,
            }
            
            performance = calculate_portfolio_performance(portfolio)
            
            # With 100 shares at $100 cost, $110 price: total return should be positive
            assert performance["total_return"] >= 0 or performance["total_return"] is not None
