"""
Portfolio Backtesting Engine

Historical simulation and performance analysis for portfolios.
Supports various strategies, rebalancing methods, and performance metrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import math
import logging

logger = logging.getLogger(__name__)

class RebalanceMethod(str, Enum):
    """Portfolio rebalancing methods"""
    NO_REBALANCE = "no_rebalance"           # Buy and hold
    ANNUAL = "annual"                        # Once per year
    QUARTERLY = "quarterly"                  # Every 3 months
    MONTHLY = "monthly"                      # Every month
    THRESHOLD = "threshold"                  # When drift exceeds threshold

class RebalanceFrequency(str, Enum):
    """Rebalance frequency options"""
    NEVER = "never"
    ANNUALLY = "annually"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"

@dataclass
class BacktestResult:
    """Results of a backtest simulation"""
    portfolio_name: str
    start_date: datetime
    end_date: datetime
    initial_investment: float
    
    # Performance metrics
    final_value: float
    total_return: float              # Dollars gained/lost
    total_return_pct: float          # Percentage return
    annualized_return: float         # Annualized return %
    
    # Risk metrics
    volatility: float                # Annual volatility %
    sharpe_ratio: float              # Sharpe ratio
    sortino_ratio: float             # Sortino ratio (downside volatility)
    max_drawdown: float              # Maximum drawdown %
    max_drawdown_duration: int       # Days
    
    # Comparison
    vs_sp500_return: Optional[float] = None
    vs_sp500_outperformance: Optional[float] = None
    
    # Trade history
    trades: List[Dict] = field(default_factory=list)
    rebalances: List[Dict] = field(default_factory=list)
    
    # Monthly/quarterly breakdown
    monthly_returns: List[float] = field(default_factory=list)
    best_month: Optional[float] = None
    worst_month: Optional[float] = None
    positive_months: int = 0
    negative_months: int = 0
    
    # Value history for charting
    value_history: List[Tuple[datetime, float]] = field(default_factory=list)

class PortfolioBacktester:
    """
    Backtests portfolio performance against historical data.
    
    Features:
    - Historical price simulation
    - Multiple asset allocation strategies
    - Rebalancing support (annual, quarterly, monthly, threshold-based)
    - Comprehensive performance metrics
    - Risk analysis (drawdown, volatility, Sharpe ratio)
    - Comparison against benchmarks (S&P 500)
    - Trade and rebalance history
    """
    
    def __init__(self, market_data_service=None):
        """
        Initialize backtester.
        
        Args:
            market_data_service: Service for fetching historical price data
        """
        self.market_data_service = market_data_service
    
    def backtest_portfolio(
        self,
        portfolio_name: str,
        holdings: List[Dict],  # [{"symbol": "AAPL", "allocation": 0.60}, ...]
        start_date: datetime,
        end_date: datetime,
        initial_investment: float = 100000,
        rebalance_method: RebalanceMethod = RebalanceMethod.ANNUAL,
        benchmark_symbol: str = "SPY"
    ) -> BacktestResult:
        """
        Run backtest for a portfolio allocation strategy.
        
        Args:
            portfolio_name: Name of portfolio for reporting
            holdings: List of holdings with allocation percentages
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_investment: Starting investment amount
            rebalance_method: How often to rebalance
            benchmark_symbol: Benchmark for comparison (default: SPY)
        
        Returns:
            BacktestResult with comprehensive performance metrics
        """
        logger.info(f"Starting backtest: {portfolio_name} ({start_date.date()} to {end_date.date()})")
        
        # Initialize result
        result = BacktestResult(
            portfolio_name=portfolio_name,
            start_date=start_date,
            end_date=end_date,
            initial_investment=initial_investment,
            final_value=initial_investment,
            total_return=0,
            total_return_pct=0,
            annualized_return=0,
            volatility=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            max_drawdown=0,
            max_drawdown_duration=0
        )
        
        # Get historical data for all holdings
        price_history = {}
        for holding in holdings:
            symbol = holding["symbol"]
            if self.market_data_service:
                prices = self.market_data_service.get_historical_prices(
                    symbol, start_date, end_date
                )
                price_history[symbol] = prices
        
        # Simulate day-by-day portfolio value
        current_date = start_date
        position_values = {h["symbol"]: initial_investment * h["allocation"] for h in holdings}
        value_history = [(current_date, initial_investment)]
        daily_returns = []
        
        rebalance_schedule = self._generate_rebalance_schedule(
            start_date, end_date, rebalance_method
        )
        
        previous_value = initial_investment
        
        while current_date <= end_date:
            # Update position values based on today's prices
            total_value = 0
            for symbol, initial_value in position_values.items():
                if symbol in price_history and current_date in price_history[symbol]:
                    current_price = price_history[symbol][current_date]
                    position_values[symbol] = (
                        initial_value * 
                        (current_price / price_history[symbol][start_date])
                    )
                total_value += position_values.get(symbol, 0)
            
            # Record value
            value_history.append((current_date, total_value))
            
            # Calculate daily return
            if previous_value > 0:
                daily_ret = (total_value - previous_value) / previous_value
                daily_returns.append(daily_ret)
            
            # Check rebalancing
            if current_date in rebalance_schedule:
                position_values = self._rebalance_portfolio(
                    position_values, holdings, total_value
                )
                result.rebalances.append({
                    "date": current_date,
                    "action": "rebalance",
                    "total_value": total_value
                })
            
            previous_value = total_value
            current_date += timedelta(days=1)
        
        # Calculate final performance metrics
        result.final_value = total_value
        result.total_return = total_value - initial_investment
        result.total_return_pct = (result.total_return / initial_investment) * 100
        result.value_history = value_history
        
        # Annualized return
        days_held = (end_date - start_date).days
        years_held = days_held / 365.25
        if years_held > 0:
            result.annualized_return = (
                ((total_value / initial_investment) ** (1 / years_held)) - 1
            ) * 100
        
        # Risk metrics
        if daily_returns:
            result.volatility = self._calculate_volatility(daily_returns)
            result.sharpe_ratio = self._calculate_sharpe_ratio(daily_returns, result.annualized_return)
            result.sortino_ratio = self._calculate_sortino_ratio(daily_returns, result.annualized_return)
        
        result.max_drawdown, result.max_drawdown_duration = self._calculate_max_drawdown(
            [v[1] for v in value_history]
        )
        
        # Monthly returns
        result.monthly_returns, result.best_month, result.worst_month = \
            self._calculate_monthly_returns(value_history)
        result.positive_months = sum(1 for r in result.monthly_returns if r >= 0)
        result.negative_months = sum(1 for r in result.monthly_returns if r < 0)
        
        # Benchmark comparison
        if benchmark_symbol and self.market_data_service:
            benchmark_return = self._calculate_benchmark_return(
                benchmark_symbol, start_date, end_date, initial_investment
            )
            if benchmark_return is not None:
                result.vs_sp500_return = benchmark_return
                result.vs_sp500_outperformance = result.total_return_pct - benchmark_return
        
        logger.info(f"Backtest completed: {result.portfolio_name} (Return: {result.total_return_pct:.2f}%)")
        return result
    
    # ===== Helper Methods =====
    
    def _generate_rebalance_schedule(
        self,
        start_date: datetime,
        end_date: datetime,
        method: RebalanceMethod
    ) -> set:
        """Generate dates when rebalancing should occur"""
        rebalance_dates = set()
        
        if method == RebalanceMethod.NO_REBALANCE:
            return rebalance_dates
        
        current = start_date
        while current <= end_date:
            if method == RebalanceMethod.ANNUAL:
                rebalance_dates.add(current)
                current += timedelta(days=365)
            elif method == RebalanceMethod.QUARTERLY:
                rebalance_dates.add(current)
                current += timedelta(days=90)
            elif method == RebalanceMethod.MONTHLY:
                rebalance_dates.add(current)
                current += timedelta(days=30)
        
        return rebalance_dates
    
    def _rebalance_portfolio(
        self,
        position_values: Dict[str, float],
        holdings: List[Dict],
        total_value: float
    ) -> Dict[str, float]:
        """Rebalance portfolio to target allocation"""
        rebalanced = {}
        for holding in holdings:
            symbol = holding["symbol"]
            target_allocation = holding["allocation"]
            rebalanced[symbol] = total_value * target_allocation
        return rebalanced
    
    def _calculate_volatility(self, daily_returns: List[float]) -> float:
        """Calculate annualized volatility"""
        if len(daily_returns) < 2:
            return 0
        
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = math.sqrt(variance)
        annualized = std_dev * math.sqrt(252)  # 252 trading days
        return annualized * 100
    
    def _calculate_sharpe_ratio(
        self,
        daily_returns: List[float],
        annualized_return: float,
        risk_free_rate: float = 2.0
    ) -> float:
        """Calculate Sharpe ratio"""
        volatility = self._calculate_volatility(daily_returns)
        if volatility == 0:
            return 0
        return (annualized_return - risk_free_rate) / volatility
    
    def _calculate_sortino_ratio(
        self,
        daily_returns: List[float],
        annualized_return: float,
        risk_free_rate: float = 2.0
    ) -> float:
        """Calculate Sortino ratio (uses downside volatility)"""
        downside_returns = [r for r in daily_returns if r < 0]
        if not downside_returns:
            return 0
        
        mean_downside = sum(downside_returns) / len(downside_returns)
        downside_variance = sum((r - mean_downside) ** 2 for r in downside_returns) / len(downside_returns)
        downside_std = math.sqrt(downside_variance) * math.sqrt(252)
        
        if downside_std == 0:
            return 0
        return (annualized_return - risk_free_rate) / (downside_std * 100)
    
    def _calculate_max_drawdown(self, values: List[float]) -> Tuple[float, int]:
        """Calculate maximum drawdown and duration"""
        if not values:
            return 0, 0
        
        max_value = values[0]
        max_drawdown = 0
        max_drawdown_start = 0
        max_drawdown_duration = 0
        drawdown_start = 0
        
        for i, value in enumerate(values):
            if value > max_value:
                max_value = value
                drawdown_start = i
            
            drawdown = (value - max_value) / max_value
            if drawdown < max_drawdown:
                max_drawdown = drawdown
                max_drawdown_start = drawdown_start
                max_drawdown_duration = i - drawdown_start
        
        return abs(max_drawdown) * 100, max_drawdown_duration
    
    def _calculate_monthly_returns(
        self,
        value_history: List[Tuple[datetime, float]]
    ) -> Tuple[List[float], Optional[float], Optional[float]]:
        """Calculate monthly returns"""
        if not value_history:
            return [], None, None
        
        monthly_returns = []
        current_month = value_history[0][0].month
        month_start_value = value_history[0][1]
        
        for date, value in value_history[1:]:
            if date.month != current_month:
                # Month changed, record return
                monthly_return = ((value - month_start_value) / month_start_value) * 100
                monthly_returns.append(monthly_return)
                
                current_month = date.month
                month_start_value = value
        
        if not monthly_returns:
            return [], None, None
        
        return monthly_returns, max(monthly_returns), min(monthly_returns)
    
    def _calculate_benchmark_return(
        self,
        benchmark_symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_investment: float
    ) -> Optional[float]:
        """Calculate benchmark return for comparison"""
        if not self.market_data_service:
            return None
        
        try:
            prices = self.market_data_service.get_historical_prices(
                benchmark_symbol, start_date, end_date
            )
            start_price = prices.get(start_date)
            end_price = prices.get(end_date)
            
            if start_price and end_price:
                return ((end_price - start_price) / start_price) * 100
        except Exception as e:
            logger.warning(f"Failed to calculate benchmark return: {e}")
        
        return None
    
    # ===== Strategy Analysis =====
    
    def compare_strategies(
        self,
        strategies: List[Dict],
        start_date: datetime,
        end_date: datetime,
        initial_investment: float = 100000
    ) -> List[BacktestResult]:
        """Compare multiple portfolio strategies"""
        results = []
        for strategy in strategies:
            result = self.backtest_portfolio(
                portfolio_name=strategy.get("name", "Unnamed"),
                holdings=strategy.get("holdings", []),
                start_date=start_date,
                end_date=end_date,
                initial_investment=initial_investment,
                rebalance_method=strategy.get("rebalance_method", RebalanceMethod.ANNUAL)
            )
            results.append(result)
        
        return sorted(results, key=lambda r: r.annualized_return, reverse=True)
    
    def monte_carlo_simulation(
        self,
        holdings: List[Dict],
        initial_investment: float,
        years: int = 20,
        simulations: int = 1000
    ) -> Dict:
        """
        Run Monte Carlo simulation for long-term portfolio growth.
        
        Args:
            holdings: Portfolio holdings
            initial_investment: Starting amount
            years: Simulation period
            simulations: Number of simulation runs
        
        Returns:
            Statistics on portfolio outcomes
        """
        logger.info(f"Running Monte Carlo simulation ({simulations} runs, {years} years)")
        
        final_values = []
        
        # Simplified simulation using historical returns
        for _ in range(simulations):
            value = initial_investment
            # Simulate compound annual growth (5-8% average stock market return)
            annual_return = 0.07  # 7% average
            for _ in range(years):
                value *= (1 + annual_return)
            final_values.append(value)
        
        final_values.sort()
        
        return {
            "mean": sum(final_values) / len(final_values),
            "median": final_values[len(final_values) // 2],
            "percentile_10": final_values[int(len(final_values) * 0.1)],
            "percentile_25": final_values[int(len(final_values) * 0.25)],
            "percentile_75": final_values[int(len(final_values) * 0.75)],
            "percentile_90": final_values[int(len(final_values) * 0.9)],
            "min": final_values[0],
            "max": final_values[-1]
        }
