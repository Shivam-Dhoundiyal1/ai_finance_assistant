"""
Alert & Backtesting API Endpoints

Exposes portfolio alerts system and backtesting engine via REST/WebSocket APIs.
"""

from fastapi import APIRouter, HTTPException, WebSocketException, WebSocket, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.data.alerts import (
    get_alert_manager,
    AlertRule,
    Alert,
    AlertType,
    AlertSeverity,
    NotificationChannel
)
from src.data.backtesting import (
    PortfolioBacktester,
    BacktestResult,
    RebalanceMethod
)
from src.core.conversation_context import get_conversation_store
from src.api.websocket_manager import manager as ws_manager

logger = logging.getLogger(__name__)

# ===== Pydantic Models =====

class AlertRuleRequest(BaseModel):
    """Create/update alert rule"""
    alert_type: AlertType
    portfolio_id: str
    parameters: Dict[str, Any]
    notification_channels: List[NotificationChannel]
    severity: AlertSeverity = AlertSeverity.WARNING
    check_interval: int = 3600  # Default: hourly
    min_time_between_alerts: int = 1800  # Default: 30 min
    enabled: bool = True

class AlertRuleResponse(BaseModel):
    """Alert rule response"""
    id: str
    portfolio_id: str
    alert_type: AlertType
    enabled: bool
    severity: AlertSeverity
    created_at: datetime
    last_triggered: Optional[datetime]
    trigger_count: int

class AlertResponse(BaseModel):
    """Alert response"""
    id: str
    rule_id: str
    title: str
    message: str
    severity: AlertSeverity
    triggered_at: datetime
    acknowledged: bool
    metadata: Dict[str, Any]

class BacktestRequest(BaseModel):
    """Backtest portfolio request"""
    portfolio_name: str
    holdings: List[Dict[str, Any]]  # [{"symbol": "AAPL", "allocation": 0.6}]
    start_date: datetime
    end_date: datetime
    initial_investment: float = 100000
    rebalance_method: RebalanceMethod = RebalanceMethod.ANNUAL

class StrategyComparisonRequest(BaseModel):
    """Compare multiple strategies"""
    strategies: List[Dict[str, Any]]
    start_date: datetime
    end_date: datetime
    initial_investment: float = 100000

class BacktestResultResponse(BaseModel):
    """Backtest result response"""
    portfolio_name: str
    start_date: datetime
    end_date: datetime
    initial_investment: float
    final_value: float
    total_return: float
    total_return_pct: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    vs_sp500_return: Optional[float]
    vs_sp500_outperformance: Optional[float]
    positive_months: int
    negative_months: int
    best_month: Optional[float]
    worst_month: Optional[float]

# ===== Create Router =====
router = APIRouter(prefix="/api", tags=["alerts", "backtesting"])

# ===== Alert Endpoints =====

@router.post("/alerts/rules")
async def create_alert_rule(request: AlertRuleRequest) -> AlertRuleResponse:
    """
    Create new alert rule for portfolio.
    
    Example:
        {
            "alert_type": "PRICE_TARGET",
            "portfolio_id": "portfolio-123",
            "parameters": {"symbol": "AAPL", "target_price": 200},
            "notification_channels": ["PUSH", "EMAIL"],
            "severity": "WARNING"
        }
    """
    try:
        manager = get_alert_manager()
        rule = AlertRule(
            id=f"rule-{datetime.now().timestamp()}",
            portfolio_id=request.portfolio_id,
            alert_type=request.alert_type,
            enabled=request.enabled,
            parameters=request.parameters,
            notification_channels=request.notification_channels,
            severity=request.severity,
            check_interval=request.check_interval,
            min_time_between_alerts=request.min_time_between_alerts
        )
        manager.create_rule(rule)
        
        return AlertRuleResponse(
            id=rule.id,
            portfolio_id=rule.portfolio_id,
            alert_type=rule.alert_type,
            enabled=rule.enabled,
            severity=rule.severity,
            created_at=datetime.now(),
            last_triggered=None,
            trigger_count=0
        )
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alerts/rules/{portfolio_id}")
async def get_portfolio_rules(portfolio_id: str) -> List[AlertRuleResponse]:
    """Get all alert rules for a portfolio"""
    try:
        manager = get_alert_manager()
        rules = manager.get_portfolio_rules(portfolio_id)
        
        return [
            AlertRuleResponse(
                id=rule.id,
                portfolio_id=rule.portfolio_id,
                alert_type=rule.alert_type,
                enabled=rule.enabled,
                severity=rule.severity,
                created_at=datetime.now(),
                last_triggered=rule.last_triggered,
                trigger_count=rule.trigger_count
            )
            for rule in rules
        ]
    except Exception as e:
        logger.error(f"Error retrieving alert rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/alerts/rules/{rule_id}")
async def update_alert_rule(
    rule_id: str,
    request: AlertRuleRequest
) -> AlertRuleResponse:
    """Update alert rule"""
    try:
        manager = get_alert_manager()
        manager.update_rule(rule_id, **request.dict())
        rule = manager.get_rule(rule_id)
        
        return AlertRuleResponse(
            id=rule.id,
            portfolio_id=rule.portfolio_id,
            alert_type=rule.alert_type,
            enabled=rule.enabled,
            severity=rule.severity,
            created_at=datetime.now(),
            last_triggered=rule.last_triggered,
            trigger_count=rule.trigger_count
        )
    except Exception as e:
        logger.error(f"Error updating alert rule: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/alerts/rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    """Delete alert rule"""
    try:
        manager = get_alert_manager()
        manager.delete_rule(rule_id)
        return {"status": "deleted", "rule_id": rule_id}
    except Exception as e:
        logger.error(f"Error deleting alert rule: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/alerts/rules/{rule_id}/enable")
async def enable_alert_rule(rule_id: str):
    """Enable alert rule"""
    try:
        manager = get_alert_manager()
        manager.enable_rule(rule_id)
        return {"status": "enabled", "rule_id": rule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/alerts/rules/{rule_id}/disable")
async def disable_alert_rule(rule_id: str):
    """Disable alert rule"""
    try:
        manager = get_alert_manager()
        manager.disable_rule(rule_id)
        return {"status": "disabled", "rule_id": rule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alerts/{portfolio_id}")
async def get_portfolio_alerts(
    portfolio_id: str,
    hours: int = Query(24, ge=1, le=720)
) -> List[AlertResponse]:
    """Get alerts for portfolio (last N hours)"""
    try:
        manager = get_alert_manager()
        alerts = manager.get_alert_history(portfolio_id, hours=hours)
        
        return [
            AlertResponse(
                id=alert.id,
                rule_id=alert.rule_id,
                title=alert.title,
                message=alert.message,
                severity=alert.severity,
                triggered_at=alert.triggered_at,
                acknowledged=alert.acknowledged,
                metadata=alert.metadata
            )
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/unacknowledged/{portfolio_id}")
async def get_unacknowledged_alerts(portfolio_id: str) -> List[AlertResponse]:
    """Get unacknowledged alerts for portfolio"""
    try:
        manager = get_alert_manager()
        alerts = manager.get_unacknowledged_alerts(portfolio_id)
        
        return [
            AlertResponse(
                id=alert.id,
                rule_id=alert.rule_id,
                title=alert.title,
                message=alert.message,
                severity=alert.severity,
                triggered_at=alert.triggered_at,
                acknowledged=alert.acknowledged,
                metadata=alert.metadata
            )
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Error retrieving unacknowledged alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge alert"""
    try:
        manager = get_alert_manager()
        manager.acknowledge_alert(alert_id)
        return {"status": "acknowledged", "alert_id": alert_id}
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/alerts/statistics/{portfolio_id}")
async def get_alert_statistics(portfolio_id: str):
    """Get alert statistics for portfolio"""
    try:
        manager = get_alert_manager()
        stats = manager.get_statistics(portfolio_id)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving alert statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== Backtesting Endpoints =====

@router.post("/backtest")
async def backtest_portfolio(request: BacktestRequest) -> BacktestResultResponse:
    """
    Backtest portfolio strategy.
    
    Example:
        {
            "portfolio_name": "60/40 Portfolio",
            "holdings": [
                {"symbol": "SPY", "allocation": 0.60},
                {"symbol": "BND", "allocation": 0.40}
            ],
            "start_date": "2020-01-01",
            "end_date": "2025-04-21",
            "initial_investment": 100000,
            "rebalance_method": "ANNUAL"
        }
    """
    try:
        backtester = PortfolioBacktester()
        result = backtester.backtest_portfolio(
            portfolio_name=request.portfolio_name,
            holdings=request.holdings,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_investment=request.initial_investment,
            rebalance_method=request.rebalance_method
        )
        
        return BacktestResultResponse(
            portfolio_name=result.portfolio_name,
            start_date=result.start_date,
            end_date=result.end_date,
            initial_investment=result.initial_investment,
            final_value=result.final_value,
            total_return=result.total_return,
            total_return_pct=result.total_return_pct,
            annualized_return=result.annualized_return,
            volatility=result.volatility,
            sharpe_ratio=result.sharpe_ratio,
            sortino_ratio=result.sortino_ratio,
            max_drawdown=result.max_drawdown,
            max_drawdown_duration=result.max_drawdown_duration,
            vs_sp500_return=result.vs_sp500_return,
            vs_sp500_outperformance=result.vs_sp500_outperformance,
            positive_months=result.positive_months,
            negative_months=result.negative_months,
            best_month=result.best_month,
            worst_month=result.worst_month
        )
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/backtest/compare")
async def compare_strategies(request: StrategyComparisonRequest) -> List[BacktestResultResponse]:
    """
    Compare multiple portfolio strategies.
    
    Returns results ranked by annualized return (best first).
    """
    try:
        backtester = PortfolioBacktester()
        results = backtester.compare_strategies(
            strategies=request.strategies,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_investment=request.initial_investment
        )
        
        return [
            BacktestResultResponse(
                portfolio_name=result.portfolio_name,
                start_date=result.start_date,
                end_date=result.end_date,
                initial_investment=result.initial_investment,
                final_value=result.final_value,
                total_return=result.total_return,
                total_return_pct=result.total_return_pct,
                annualized_return=result.annualized_return,
                volatility=result.volatility,
                sharpe_ratio=result.sharpe_ratio,
                sortino_ratio=result.sortino_ratio,
                max_drawdown=result.max_drawdown,
                max_drawdown_duration=result.max_drawdown_duration,
                vs_sp500_return=result.vs_sp500_return,
                vs_sp500_outperformance=result.vs_sp500_outperformance,
                positive_months=result.positive_months,
                negative_months=result.negative_months,
                best_month=result.best_month,
                worst_month=result.worst_month
            )
            for result in results
        ]
    except Exception as e:
        logger.error(f"Error comparing strategies: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/backtest/monte-carlo")
async def run_monte_carlo(
    holdings: List[Dict] = None,
    initial_investment: float = 100000,
    years: int = 20,
    simulations: int = 1000
):
    """
    Run Monte Carlo simulation for long-term projections.
    
    Returns percentile outcomes (10th, 25th, median, 75th, 90th).
    """
    try:
        backtester = PortfolioBacktester()
        results = backtester.monte_carlo_simulation(
            holdings=holdings or [],
            initial_investment=initial_investment,
            years=years,
            simulations=simulations
        )
        return results
    except Exception as e:
        logger.error(f"Error running Monte Carlo: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ===== WebSocket Alert Streaming =====

@router.websocket("/ws/alerts/{portfolio_id}")
async def websocket_alerts(websocket: WebSocket, portfolio_id: str):
    """
    WebSocket for real-time alert streaming.
    
    Connection example:
        ws://localhost:8000/ws/alerts/portfolio-123
    
    Server sends:
        {
            "type": "alert",
            "alert": {...},
            "rule": {...}
        }
    """
    await websocket.accept()
    manager = get_alert_manager()
    
    try:
        # Register this connection
        ws_manager.subscribe(f"alerts_{portfolio_id}", websocket)
        
        # Send initial unacknowledged alerts
        initial_alerts = manager.get_unacknowledged_alerts(portfolio_id)
        for alert in initial_alerts:
            await websocket.send_json({
                "type": "alert",
                "alert": {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity.value,
                    "triggered_at": alert.triggered_at.isoformat()
                }
            })
        
        # Keep connection alive and listen for acknowledgments
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "acknowledge":
                manager.acknowledge_alert(data.get("alert_id"))
                await websocket.send_json({"type": "ack", "status": "acknowledged"})
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.unsubscribe(f"alerts_{portfolio_id}", websocket)

# ===== Health Check =====

@router.get("/health/alerts")
async def health_check_alerts():
    """Health check for alert system"""
    try:
        manager = get_alert_manager()
        return {
            "status": "healthy",
            "service": "alerts",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Alert health check failed: {e}")
        raise HTTPException(status_code=503, detail="Alert service unavailable")

@router.get("/health/backtesting")
async def health_check_backtesting():
    """Health check for backtesting system"""
    try:
        backtester = PortfolioBacktester()
        return {
            "status": "healthy",
            "service": "backtesting",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Backtesting health check failed: {e}")
        raise HTTPException(status_code=503, detail="Backtesting service unavailable")
