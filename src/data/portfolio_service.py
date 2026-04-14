"""Portfolio data: user-provided or sample portfolio for analysis."""
import json
import os
from datetime import datetime
from typing import Any, Dict, List


def get_sample_portfolio() -> str:
    """Return a sample portfolio summary for demo. In production, load from user input/session."""
    return (
        "Sample portfolio (for demo):\n"
        "- Total value: $50,000\n"
        "- Allocation: 60% stocks (e.g. index funds), 30% bonds, 10% cash.\n"
        "Users can input their own holdings in the Portfolio tab for personalized analysis."
    )


def parse_user_portfolio(positions: list[dict[str, Any]]) -> dict[str, Any]:
    """Parse user-submitted positions into summary. positions: [{symbol, quantity, avg_cost}, ...]."""
    total = 0.0
    for p in positions:
        qty = float(p.get("quantity", 0))
        cost = float(p.get("avg_cost", 0))
        total += qty * cost
    return {"total_value": total, "positions": positions}


def save_portfolio(user_id: str, holdings: List[Dict[str, Any]]) -> bool:
    """Save user portfolio to file storage."""
    try:
        portfolio_data = {
            "user_id": user_id,
            "holdings": holdings,
            "total_value": sum(h["quantity"] * h.get("avg_cost", 0) for h in holdings),
            "allocation": _calculate_allocation(holdings),
            "last_updated": datetime.now().isoformat()
        }
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "portfolios")
        os.makedirs(data_dir, exist_ok=True)
        
        # Save to file
        file_path = os.path.join(data_dir, f"{user_id}_portfolio.json")
        with open(file_path, 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        return True
    except Exception:
        return False


def get_user_portfolio(user_id: str) -> Dict[str, Any]:
    """Load user portfolio from file storage."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "..", "data", "portfolios", f"{user_id}_portfolio.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Return default portfolio if none exists
            return {
                "user_id": user_id,
                "holdings": [
                    {"symbol": "AAPL", "quantity": 10, "avg_cost": 150.0},
                    {"symbol": "MSFT", "quantity": 5, "avg_cost": 250.0},
                    {"symbol": "GOOGL", "quantity": 8, "avg_cost": 120.0}
                ],
                "total_value": 50000.0,
                "allocation": {"AAPL": 30.0, "MSFT": 25.0, "GOOGL": 19.2},
                "last_updated": "Never"
            }
    except Exception:
        return {"holdings": [], "total_value": 0, "allocation": {}, "last_updated": "Error"}


def update_portfolio(user_id: str, holdings: List[Dict[str, Any]]) -> bool:
    """Update user portfolio in file storage."""
    return save_portfolio(user_id, holdings)


def delete_holding(user_id: str, symbol: str) -> bool:
    """Delete a specific holding from user portfolio."""
    try:
        portfolio = get_user_portfolio(user_id)
        portfolio["holdings"] = [h for h in portfolio["holdings"] if h["symbol"] != symbol]
        portfolio["total_value"] = sum(h["quantity"] * h.get("avg_cost", 0) for h in portfolio["holdings"])
        portfolio["allocation"] = _calculate_allocation(portfolio["holdings"])
        portfolio["last_updated"] = datetime.now().isoformat()
        
        return save_portfolio(user_id, portfolio["holdings"])
    except Exception:
        return False


def calculate_portfolio_performance(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate portfolio performance metrics."""
    if not portfolio.get("holdings"):
        return {
            "total_return": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "allocation_chart": {},
            "performance_chart": {}
        }
    
    # Basic calculations (would be enhanced with real market data)
    total_value = portfolio.get("total_value", 0)
    holdings = portfolio.get("holdings", [])
    
    # Calculate allocation chart data
    allocation_chart = {}
    for holding in holdings:
        symbol = holding["symbol"]
        value = holding["quantity"] * holding.get("avg_cost", 0)
        allocation_chart[symbol] = {
            "value": value,
            "percentage": (value / total_value * 100) if total_value > 0 else 0
        }
    
    return {
        "total_return": 0.0,  # Would calculate from current vs. purchase prices
        "annualized_return": 0.0,
        "volatility": 0.0,
        "sharpe_ratio": 0.0,
        "allocation_chart": allocation_chart,
        "performance_chart": {}  # Historical performance data
    }


def analyze_allocation(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze portfolio allocation and diversification."""
    if not portfolio.get("holdings"):
        return {
            "current_allocation": {},
            "recommended_allocation": {"stocks": 60, "bonds": 30, "cash": 10},
            "allocation_chart": {},
            "diversification_score": 0.0
        }
    
    current_allocation = portfolio.get("allocation", {})
    holdings_count = len(portfolio.get("holdings", []))
    
    # Simple diversification score based on number of holdings
    diversification_score = min(100, holdings_count * 15)
    
    return {
        "current_allocation": current_allocation,
        "recommended_allocation": {"stocks": 60, "bonds": 30, "cash": 10},
        "allocation_chart": current_allocation,
        "diversification_score": diversification_score
    }


def calculate_portfolio_metrics(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comprehensive portfolio metrics."""
    holdings = portfolio.get("holdings", [])
    total_value = portfolio.get("total_value", 0)
    
    # Enhanced metrics
    metrics = {
        "total_holdings": len(holdings),
        "diversification_score": _calculate_diversification(holdings),
        "largest_holding": _get_largest_holding(holdings),
        "sector_allocation": _estimate_sector_allocation(holdings),
        "risk_score": _calculate_risk_score(portfolio),
        "concentration_risk": _calculate_concentration_risk(holdings, total_value),
        "performance_metrics": _calculate_performance_metrics(portfolio)
    }
    
    return {**portfolio, **metrics}


def _calculate_diversification(holdings: List[Dict[str, Any]]) -> float:
    """Calculate portfolio diversification score."""
    if len(holdings) <= 1:
        return 0.0
    return min(100, len(holdings) * 15)


def _get_largest_holding(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find largest holding by value."""
    if not holdings:
        return {"symbol": "N/A", "value": 0, "percentage": 0}
    
    largest = max(holdings, key=lambda h: h["quantity"] * h.get("avg_cost", 0))
    largest_value = largest["quantity"] * largest.get("avg_cost", 0)
    total_value = sum(h["quantity"] * h.get("avg_cost", 0) for h in holdings)
    
    return {
        "symbol": largest["symbol"],
        "value": largest_value,
        "percentage": (largest_value / total_value * 100) if total_value > 0 else 0
    }


def _calculate_concentration_risk(holdings: List[Dict[str, Any]], total_value: float) -> float:
    """Calculate concentration risk (largest holding percentage)."""
    if not holdings or total_value == 0:
        return 0.0
    
    largest = _get_largest_holding(holdings)
    return largest["percentage"]


def _estimate_sector_allocation(holdings: List[Dict[str, Any]]) -> Dict[str, float]:
    """Estimate sector allocation based on common stock classifications."""
    sector_map = {
        "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
        "JPM": "Finance", "BAC": "Finance", "WFC": "Finance",
        "JNJ": "Healthcare", "PFE": "Healthcare", "UNH": "Healthcare",
        "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
        "KO": "Consumer", "PEP": "Consumer", "WMT": "Consumer"
    }
    
    sector_allocation = {}
    total_value = sum(h["quantity"] * h.get("avg_cost", 0) for h in holdings)
    
    for holding in holdings:
        symbol = holding["symbol"]
        sector = sector_map.get(symbol, "Other")
        value = holding["quantity"] * holding.get("avg_cost", 0)
        
        if sector not in sector_allocation:
            sector_allocation[sector] = 0
        sector_allocation[sector] += (value / total_value * 100) if total_value > 0 else 0
    
    return sector_allocation


def _calculate_risk_score(portfolio: Dict[str, Any]) -> float:
    """Calculate portfolio risk score based on diversification and concentration."""
    holdings = portfolio.get("holdings", [])
    
    # Base risk score
    risk_score = 50.0  # Neutral starting point
    
    # Adjust for diversification
    diversification = _calculate_diversification(holdings)
    if diversification > 50:
        risk_score -= 10  # Lower risk for good diversification
    elif diversification < 20:
        risk_score += 20  # Higher risk for poor diversification
    
    # Adjust for concentration
    concentration = _calculate_concentration_risk(holdings, portfolio.get("total_value", 0))
    if concentration > 40:
        risk_score += 15  # Higher risk for concentration
    elif concentration < 20:
        risk_score -= 5  # Lower risk for good balance
    
    return max(0, min(100, risk_score))


def _calculate_performance_metrics(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate portfolio performance metrics (placeholder for future enhancement)."""
    return {
        "total_return": 0.0,  # Would calculate from current vs. purchase prices
        "annualized_return": 0.0,
        "volatility": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "win_rate": 0.0  # Would track profitable vs. unprofitable periods
    }


def _calculate_allocation(holdings: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate portfolio allocation percentages."""
    if not holdings:
        return {}
    
    total_value = sum(h["quantity"] * h.get("avg_cost", 0) for h in holdings)
    allocation = {}
    
    for holding in holdings:
        symbol = holding["symbol"]
        value = holding["quantity"] * holding.get("avg_cost", 0)
        allocation[symbol] = (value / total_value * 100) if total_value > 0 else 0
    
    return allocation
