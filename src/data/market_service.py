"""Market data: yfinance quotes, symbols extraction, and caching."""
import time
from functools import lru_cache
from typing import Dict, Any, Optional

import requests
import yfinance as yf

from src.core.config import get_settings


class MarketDataCache:
    """Multi-layer market data caching system."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached market data if available and not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if isinstance(entry, dict) and "data" in entry and "timestamp" in entry:
                data = entry["data"]
                timestamp = entry["timestamp"]
            else:
                data, timestamp = entry
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


def _fetch_from_tavily(symbol: str) -> Dict[str, Any]:
    """Use Tavily search as a fallback when market APIs fail to return a quote."""
    s = get_settings()
    if not s.tavily_api_key:
        return {"error": "Tavily API key not configured"}

    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": s.tavily_api_key,
            "query": f"{symbol} stock price current quote",
            "search_depth": "basic",
            "max_results": 3,
            "include_answer": True,
            "include_raw_content": False,
        }
        response = requests.post(url, json=payload, timeout=12)
        if response.status_code != 200:
            return {"error": f"Tavily API Error: {response.status_code}"}

        data = response.json()
        answer = data.get("answer") or ""
        results = data.get("results") or []
        text_snippet = "\n".join(item.get("content", "") for item in results if item.get("content"))
        merged = f"{answer}\n{text_snippet}".strip()

        price_match = None
        for pattern in [r"\$\s?(\d+(?:\.\d+)?)", r"\b(\d+(?:\.\d+)?)\s*USD\b", r"\b(\d+(?:\.\d+)?)\s*per share\b"]:
            match = __import__("re").search(pattern, merged, __import__("re").IGNORECASE)
            if match:
                price_match = float(match.group(1))
                break

        if price_match is None:
            return {"error": "No quote found in Tavily search results"}

        return {
            "symbol": symbol.upper(),
            "price": price_match,
            "change": 0.0,
            "change_percent": 0.0,
            "currency": "USD",
            "source": "tavily",
            "timestamp": time.time(),
        }
    except requests.exceptions.RequestException:
        return {"error": "Tavily network error"}
    except Exception:
        return {"error": "Tavily lookup failed"}


@lru_cache(maxsize=1000)
def get_real_time_quote(symbol: str) -> Dict[str, Any]:
    """Get real-time quote with intelligent caching."""
    cache_key = f"quote_{symbol}"
    
    # Try cache first
    cached_data = market_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch from API with rate limit handling
    try:
        s = get_settings()
        if s.alpha_vantage_api_key:
            data = _fetch_from_alpha_vantage(symbol)
            if not data.get("error"):
                market_cache.set(cache_key, data)
                return data

        # Fallback to Tavily search when API-backed market data fails
        tavily_data = _fetch_from_tavily(symbol)
        if not tavily_data.get("error"):
            market_cache.set(cache_key, tavily_data)
            return tavily_data

        # Final fallback to yfinance
        data = get_quote(symbol)
        if not data.get("error"):
            market_cache.set(cache_key, data)
        return data
            
    except Exception:
        # Fallback to cached data if available
        fallback_data = market_cache.get(cache_key)
        if fallback_data:
            return fallback_data

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
    """Extract real ticker symbols while ignoring filler/market words and common English terms."""
    import re

    text = message.upper()
    banned_terms = {
        "PRICE", "PRICES", "STOCK", "STOCKS", "MARKET", "QUOTE", "QUOTES",
        "TRADING", "TICKER", "SYMBOL", "CURRENT", "LAST", "LIVE", "DATA",
        "INDEX", "SECTOR", "PORTFOLIO", "INVESTMENT", "FINANCE", "ECONOMY",
        "WHAT", "WHY", "WHEN", "WHERE", "WHICH", "HOW", "IS", "ARE", "THE", "OF",
        "AND", "OR", "FOR", "TO", "FROM", "WITH", "IN", "ON", "AT", "IT", "THIS",
        "THAT", "THERE", "HAVE", "HAS", "BUY", "SELL", "GET", "SHOW", "TELL",
        "ME", "CAN", "YOU", "DO", "PLEASE", "A", "AN",
    }

    pattern = r"(?:^|[^A-Z])\$?([A-Z]{1,5})(?=\s|$|[^A-Z])"
    matches = re.findall(pattern, text)

    forbidden_company_names = {
        "APPLE", "MICROSOFT", "GOOGLE", "AMAZON", "TESLA", "NETFLIX", "NVIDIA",
        "META", "INTEL", "AMD", "FACEBOOK", "CITIGROUP", "BANK", "MONEY",
        "STOCK", "SHARE", "PRICE", "QUOTE", "MARKET", "CURRENT", "LIVE",
    }

    symbols = set()
    for symbol in matches:
        if len(symbol) == 1:
            continue
        if len(symbol) >= 2 and len(symbol) <= 5 and symbol not in banned_terms and symbol not in forbidden_company_names:
            symbols.add(symbol)

    return sorted(symbols)


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
