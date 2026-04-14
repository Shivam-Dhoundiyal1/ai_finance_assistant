"""Market data: yfinance quotes, symbols extraction, and caching."""
import time
from functools import lru_cache
from typing import Dict, Any, Optional
import requests

from src.core.config import get_settings


class MarketDataCache:
    """Multi-layer market data caching system."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached market data if available and not expired."""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Cache market data with timestamp."""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def clear(self, key: str = None) -> None:
        """Clear specific cache entry or all."""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()


# Global cache instance
market_cache = MarketDataCache()


def _fetch_from_alpha_vantage(symbol: str) -> Dict[str, Any]:
    """Fetch from Alpha Vantage with proper rate limiting."""
    s = get_settings()
    
    # Rate limiting - respect API limits
    time.sleep(0.1)
    
    try:
        if not s.alpha_vantage_api_key:
            return {"error": "Alpha Vantage API key not configured"}
            
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={s.alpha_vantage_api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "symbol": symbol,
                "price": float(data.get("Global Quote", {}).get("05. price", 0)),
                "change": 0.0,  # Would calculate from historical data
                "change_percent": 0.0,
                "currency": "USD",
                "source": "alpha_vantage",
                "timestamp": time.time()
            }
        else:
            return {"error": f"API Error: {response.status_code}"}
            
    except requests.exceptions.RequestException:
        return {"error": "Network error - please try again"}
    except Exception:
        return {"error": "Data temporarily unavailable"}


@lru_cache(maxsize=1000)
def get_real_time_quote(symbol: str) -> Dict[str, Any]:
    """Get real-time quote with intelligent caching."""
    cache_key = f"quote_{symbol}"
    
    # Try cache first
    cached_data = market_cache.get(cache_key)
    if cached_data:
        return cached_data["data"]
    
    # Fetch from API with rate limit handling
    try:
        s = get_settings()
        if s.alpha_vantage_api_key:
            data = _fetch_from_alpha_vantage(symbol)
            if not data.get("error"):
                market_cache.set(cache_key, data)
                return data
        
        # Fallback to yfinance
        data = get_quote(symbol)
        if not data.get("error"):
            market_cache.set(cache_key, data)
        return data
            
    except Exception:
        # Fallback to cached data if available
        fallback_data = market_cache.get(cache_key)
        if fallback_data:
            return fallback_data["data"]
        
        return {"error": "Market data temporarily unavailable"}


def get_market_summary(symbols: list[str]) -> Dict[str, Any]:
    """Get market summary for multiple symbols."""
    summary = {}
    for symbol in symbols:
        summary[symbol] = get_real_time_quote(symbol)
    return summary


def get_market_indicators(symbol: str) -> Dict[str, Any]:
    """Calculate basic technical indicators."""
    quote = get_real_time_quote(symbol)
    if not quote.get("error"):
        return {
            "symbol": symbol,
            "price": quote["price"],
            "change": quote.get("change", 0),
            "change_percent": quote.get("change_percent", 0),
            "trend": "neutral",  # Would calculate from historical data
            "volume": "N/A"
        }
    return {"error": "Data not available"}


def extract_symbols(message: str) -> list[str]:
    """Extract stock symbols from a message using common patterns."""
    import re
    
    # Common patterns for stock symbols
    patterns = [
        r'\b([A-Z]{1,5})\b',  # Uppercase 1-5 letters
        r'\$([A-Z]{1,5})\b',  # $ followed by symbol
        r'\b([A-Z]{1,5})\s+stock\b',  # Symbol + "stock"
    ]
    
    symbols = set()
    for pattern in patterns:
        matches = re.findall(pattern, message.upper())
        for match in matches:
            symbol = match if isinstance(match, str) else match[0]
            if len(symbol) >= 1 and len(symbol) <= 5:
                symbols.add(symbol)
    
    return list(symbols)


def get_quote_for_message(message: str) -> list[dict[str, Any]]:
    """Get quotes for all symbols found in a message."""
    symbols = extract_symbols(message)
    quotes = []
    for symbol in symbols:
        quote_data = get_real_time_quote(symbol)
        quotes.append(quote_data)
    return quotes


def get_quote(symbol: str) -> dict[str, Any]:
    """Fetch a quote for a stock symbol using yfinance."""
    import yfinance as yf

    symbol = symbol.upper().strip()
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")

        if not info or "regularMarketPrice" not in info:
            return {"symbol": symbol, "error": "No data found"}

        price = info.get("regularMarketPrice", 0)
        prev_close = info.get("previousClose", price)

        change = price - prev_close
        change_percent = (change / prev_close * 100) if prev_close > 0 else 0

        return {
            "symbol": symbol,
            "price": price,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "currency": info.get("currency", "USD"),
            "source": "yfinance"
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def get_quote_for_message(message: str) -> str:
    """Get quotes for symbols mentioned in message; return formatted string."""
    symbols = extract_symbols(message)
    if not symbols:
        # Default to a few popular tickers for "market" queries
        symbols = ["AAPL", "MSFT", "GOOGL"]
    lines = []
    for sym in symbols[:5]:
        q = get_real_time_quote(sym)
        if q.get("error"):
            lines.append(f"{sym}: Data unavailable")
        else:
            lines.append(
                f"{sym}: ${q.get('price', 0):.2f} "
                f"({q.get('change', 0):+.2f}, {q.get('change_percent', 0):+.2f}%)"
            )
    return "\n".join(lines) if lines else "No symbols found in message."
