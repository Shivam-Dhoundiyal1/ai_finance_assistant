"""
Portfolio Alerts System

Real-time monitoring and alerting for portfolio changes, risk thresholds,
and market events. Supports multiple alert types and notification channels.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List, Callable
import asyncio
import logging

logger = logging.getLogger(__name__)

class AlertType(str, Enum):
    """Types of alerts"""
    PRICE_TARGET = "price_target"              # Stock reaches target price
    LOSS_THRESHOLD = "loss_threshold"          # Losses exceed threshold
    GAIN_TARGET = "gain_target"                # Gains reach target
    VOLATILITY = "volatility"                  # Volatility spike
    REBALANCE = "rebalance"                    # Portfolio drift from target
    DIVIDEND = "dividend"                      # Dividend payment
    NEWS = "news"                              # Important news
    SECTOR_ALERT = "sector_alert"              # Sector performance alert
    CORRELATION_CHANGE = "correlation_change"  # Correlation shift
    RISK_SPIKE = "risk_spike"                  # Risk metrics spike

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

@dataclass
class AlertRule:
    """Configuration for an alert rule"""
    id: str
    portfolio_id: str
    alert_type: AlertType
    enabled: bool = True
    
    # Condition parameters (vary by alert type)
    parameters: dict = field(default_factory=dict)
    # e.g., for PRICE_TARGET: {"symbol": "AAPL", "target_price": 200}
    # e.g., for LOSS_THRESHOLD: {"percentage": -20}
    # e.g., for REBALANCE: {"drift_threshold": 5}
    
    # Notification settings
    notification_channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.IN_APP])
    severity: AlertSeverity = AlertSeverity.INFO
    
    # Frequency settings
    check_interval: int = 3600  # Seconds (default: hourly)
    min_time_between_alerts: int = 300  # Minimum seconds between alerts (prevent spam)
    
    # Creation metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def is_due_for_check(self) -> bool:
        """Check if alert is due for evaluation"""
        if not self.enabled:
            return False
        return True
    
    def can_trigger(self) -> bool:
        """Check if alert can trigger (respects min_time_between_alerts)"""
        if not self.last_triggered:
            return True
        elapsed = (datetime.now() - self.last_triggered).total_seconds()
        return elapsed >= self.min_time_between_alerts
    
    def mark_triggered(self):
        """Mark alert as just triggered"""
        self.last_triggered = datetime.now()
        self.trigger_count += 1

@dataclass
class Alert:
    """An alert event that was triggered"""
    id: str
    rule_id: str
    portfolio_id: str
    alert_type: AlertType
    severity: AlertSeverity
    
    title: str
    message: str
    metadata: dict = field(default_factory=dict)
    # e.g., {"symbol": "AAPL", "current_price": 198, "target_price": 200}
    
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    
    notification_results: dict = field(default_factory=dict)
    # e.g., {"email": "sent", "push": "failed"}

class PortfolioAlertManager:
    """
    Manages alert rules and evaluates portfolio conditions to trigger alerts.
    
    Features:
    - Multiple alert types (price, loss, gain, volatility, rebalance, etc.)
    - Flexible rule configuration
    - Multi-channel notifications
    - Alert history and acknowledgment
    - Spam prevention with time-based throttling
    """
    
    def __init__(self):
        self.rules: dict[str, AlertRule] = {}  # rule_id -> AlertRule
        self.alerts: dict[str, Alert] = {}      # alert_id -> Alert
        self.notification_handlers: dict[NotificationChannel, Callable] = {}
        self._check_tasks: dict[str, asyncio.Task] = {}
    
    # ===== Rule Management =====
    
    def create_rule(self, rule: AlertRule) -> AlertRule:
        """Create a new alert rule"""
        self.rules[rule.id] = rule
        logger.info(f"Alert rule created: {rule.id} ({rule.alert_type})")
        return rule
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get alert rule by ID"""
        return self.rules.get(rule_id)
    
    def get_portfolio_rules(self, portfolio_id: str) -> List[AlertRule]:
        """Get all rules for a portfolio"""
        return [r for r in self.rules.values() if r.portfolio_id == portfolio_id]
    
    def update_rule(self, rule_id: str, **kwargs) -> Optional[AlertRule]:
        """Update alert rule"""
        rule = self.rules.get(rule_id)
        if not rule:
            return None
        
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.updated_at = datetime.now()
        logger.info(f"Alert rule updated: {rule_id}")
        return rule
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Alert rule deleted: {rule_id}")
            return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable an alert rule"""
        rule = self.rules.get(rule_id)
        if rule:
            rule.enabled = True
            rule.updated_at = datetime.now()
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable an alert rule"""
        rule = self.rules.get(rule_id)
        if rule:
            rule.enabled = False
            rule.updated_at = datetime.now()
            return True
        return False
    
    # ===== Alert Triggering =====
    
    def trigger_alert(self, rule: AlertRule, title: str, message: str, 
                     metadata: dict) -> Alert:
        """Trigger an alert based on a rule"""
        
        # Check if rule can trigger (throttle spam)
        if not rule.can_trigger():
            logger.debug(f"Alert rule {rule.id} throttled (too soon)")
            return None
        
        # Create alert event
        import uuid
        alert_id = f"alert-{uuid.uuid4()}"
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            portfolio_id=rule.portfolio_id,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=title,
            message=message,
            metadata=metadata
        )
        
        # Store alert
        self.alerts[alert_id] = alert
        
        # Mark rule as triggered
        rule.mark_triggered()
        
        # Send notifications
        self._send_notifications(alert, rule)
        
        logger.info(f"Alert triggered: {alert_id} ({alert.alert_type})")
        return alert
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark alert as acknowledged by user"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now()
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        return self.alerts.get(alert_id)
    
    def get_unacknowledged_alerts(self, portfolio_id: str) -> List[Alert]:
        """Get unacknowledged alerts for portfolio"""
        return [
            a for a in self.alerts.values()
            if a.portfolio_id == portfolio_id and not a.acknowledged
        ]
    
    def get_alert_history(self, portfolio_id: str, hours: int = 24) -> List[Alert]:
        """Get alert history for portfolio (last N hours)"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            a for a in self.alerts.values()
            if a.portfolio_id == portfolio_id and a.triggered_at >= cutoff
        ]
    
    # ===== Notifications =====
    
    def register_notification_handler(self, channel: NotificationChannel, 
                                      handler: Callable) -> None:
        """Register a handler for notification delivery"""
        self.notification_handlers[channel] = handler
        logger.info(f"Notification handler registered: {channel}")
    
    def _send_notifications(self, alert: Alert, rule: AlertRule) -> None:
        """Send notifications through configured channels"""
        for channel in rule.notification_channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    result = handler(alert, rule)
                    alert.notification_results[channel.value] = "sent" if result else "failed"
                except Exception as e:
                    logger.error(f"Failed to send notification ({channel}): {e}")
                    alert.notification_results[channel.value] = "error"
            else:
                logger.warning(f"No handler for notification channel: {channel}")
    
    # ===== Portfolio Monitoring =====
    
    def check_price_target(self, rule: AlertRule, current_price: float) -> Optional[Alert]:
        """Check if current price reached target"""
        target_price = rule.parameters.get("target_price")
        symbol = rule.parameters.get("symbol")
        
        if not target_price or not symbol:
            return None
        
        # Check if target reached
        if current_price >= target_price:
            return self.trigger_alert(
                rule=rule,
                title=f"{symbol} Price Target Reached",
                message=f"{symbol} has reached your target price of ${target_price}. Current: ${current_price}",
                metadata={"symbol": symbol, "target_price": target_price, "current_price": current_price}
            )
        
        return None
    
    def check_loss_threshold(self, rule: AlertRule, current_value: float, 
                           purchase_value: float) -> Optional[Alert]:
        """Check if losses exceed threshold"""
        threshold_pct = rule.parameters.get("percentage", -20)
        
        loss_pct = ((current_value - purchase_value) / purchase_value) * 100
        
        if loss_pct <= threshold_pct:
            symbol = rule.parameters.get("symbol", "Position")
            return self.trigger_alert(
                rule=rule,
                title=f"Loss Threshold Alert: {symbol}",
                message=f"Your {symbol} position has declined {loss_pct:.1f}%, exceeding your {threshold_pct}% threshold.",
                metadata={"symbol": symbol, "loss_percentage": loss_pct, "threshold": threshold_pct}
            )
        
        return None
    
    def check_rebalance_needed(self, rule: AlertRule, current_allocation: dict, 
                              target_allocation: dict) -> Optional[Alert]:
        """Check if portfolio drift exceeds rebalance threshold"""
        drift_threshold = rule.parameters.get("drift_threshold", 5)
        
        # Calculate max drift
        max_drift = 0
        for asset, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset, 0)
            drift = abs(current_pct - target_pct)
            max_drift = max(max_drift, drift)
        
        if max_drift >= drift_threshold:
            return self.trigger_alert(
                rule=rule,
                title="Portfolio Rebalancing Needed",
                message=f"Your portfolio has drifted {max_drift:.1f}% from target allocation (threshold: {drift_threshold}%).",
                metadata={"max_drift": max_drift, "threshold": drift_threshold}
            )
        
        return None
    
    def check_volatility_spike(self, rule: AlertRule, current_volatility: float,
                              baseline_volatility: float) -> Optional[Alert]:
        """Check if volatility exceeds threshold"""
        spike_threshold = rule.parameters.get("spike_percentage", 50)
        
        spike_pct = ((current_volatility - baseline_volatility) / baseline_volatility) * 100
        
        if spike_pct >= spike_threshold:
            return self.trigger_alert(
                rule=rule,
                title="Market Volatility Spike",
                message=f"Portfolio volatility has increased {spike_pct:.1f}%, exceeding your {spike_threshold}% threshold.",
                metadata={"spike_percentage": spike_pct, "threshold": spike_threshold}
            )
        
        return None
    
    # ===== Statistics =====
    
    def get_statistics(self, portfolio_id: str) -> dict:
        """Get alert statistics for portfolio"""
        rules = self.get_portfolio_rules(portfolio_id)
        alerts = self.get_alert_history(portfolio_id)
        unacked = self.get_unacknowledged_alerts(portfolio_id)
        
        return {
            "total_rules": len(rules),
            "enabled_rules": sum(1 for r in rules if r.enabled),
            "total_alerts": len(alerts),
            "unacknowledged_alerts": len(unacked),
            "critical_alerts": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
            "alerts_by_type": {
                alert_type.value: sum(1 for a in alerts if a.alert_type == alert_type)
                for alert_type in AlertType
            }
        }

# Singleton instance
_alert_manager = PortfolioAlertManager()

def get_alert_manager() -> PortfolioAlertManager:
    """Get the global alert manager instance"""
    return _alert_manager
