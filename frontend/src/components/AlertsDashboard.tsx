import React, { useState, useEffect } from 'react';
import { Bell, X, CheckCircle, AlertCircle, AlertTriangle, Info, Plus, Trash2 } from 'lucide-react';
import axios from 'axios';

interface Alert {
  id: string;
  rule_id: string;
  title: string;
  message: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  triggered_at: string;
  acknowledged: boolean;
  metadata: Record<string, any>;
}

interface AlertRule {
  id: string;
  portfolio_id: string;
  alert_type: string;
  enabled: boolean;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  created_at: string;
  last_triggered?: string;
  trigger_count: number;
}

interface AlertsDashboardProps {
  portfolio_id: string;
  onAlertClick?: (alert: Alert) => void;
}

/**
 * Alerts Dashboard Component
 *
 * Features:
 * - Real-time alert display
 * - Alert filtering and sorting
 * - Alert rules management
 * - WebSocket support for live updates
 * - Alert acknowledgment
 */
export const AlertsDashboard: React.FC<AlertsDashboardProps> = ({ portfolio_id, onAlertClick }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [view, setView] = useState<'alerts' | 'rules'>('alerts');
  const [filter, setFilter] = useState<'all' | 'unacknowledged' | 'critical'>('unacknowledged');
  const [showNewRuleForm, setShowNewRuleForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Fetch alerts
  useEffect(() => {
    fetchAlerts();
    
    // Set up WebSocket for real-time updates
    const setupWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://localhost:8000/ws/alerts/${portfolio_id}`);
        
        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          
          if (message.type === 'alert') {
            // New alert received
            setAlerts(prev => [message.alert, ...prev]);
          }
        };
        
        return ws;
      } catch (error) {
        console.error('Failed to establish WebSocket connection:', error);
        return null;
      }
    };

    const ws = setupWebSocket();
    
    return () => {
      if (ws) ws.close();
    };
  }, [portfolio_id]);

  // Fetch rules
  useEffect(() => {
    fetchRules();
  }, [portfolio_id]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/alerts/${portfolio_id}?hours=24`);
      setAlerts(response.data);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRules = async () => {
    try {
      const response = await axios.get(`/api/alerts/rules/${portfolio_id}`);
      setRules(response.data);
    } catch (error) {
      console.error('Failed to fetch alert rules:', error);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await axios.post(`/api/alerts/${alertId}/acknowledge`);
      setAlerts(alerts.map(a => 
        a.id === alertId ? { ...a, acknowledged: true } : a
      ));
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    try {
      await axios.delete(`/api/alerts/rules/${ruleId}`);
      setRules(rules.filter(r => r.id !== ruleId));
    } catch (error) {
      console.error('Failed to delete rule:', error);
    }
  };

  const handleToggleRule = async (ruleId: string, enabled: boolean) => {
    try {
      const endpoint = enabled ? 'disable' : 'enable';
      await axios.post(`/api/alerts/rules/${ruleId}/${endpoint}`);
      setRules(rules.map(r => 
        r.id === ruleId ? { ...r, enabled: !enabled } : r
      ));
    } catch (error) {
      console.error('Failed to toggle rule:', error);
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'unacknowledged') return !alert.acknowledged;
    if (filter === 'critical') return alert.severity === 'CRITICAL';
    return true;
  });

  const unacknowledgedCount = alerts.filter(a => !a.acknowledged).length;
  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL').length;

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Bell className="w-8 h-8 text-gray-600" />
              {unacknowledgedCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {unacknowledgedCount}
                </span>
              )}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Alerts</h2>
              <p className="text-sm text-gray-600">
                {unacknowledgedCount} unacknowledged • {criticalCount} critical
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setShowNewRuleForm(!showNewRuleForm)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4" />
            New Alert Rule
          </button>
        </div>

        {/* View Tabs */}
        <div className="flex gap-2 border-t border-gray-200 mt-4 pt-4">
          {(['alerts', 'rules'] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-2 font-semibold transition ${
                view === v
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts View */}
      {view === 'alerts' && (
        <AlertsView 
          alerts={filteredAlerts}
          filter={filter}
          onFilterChange={setFilter}
          onAcknowledge={handleAcknowledgeAlert}
          onAlertClick={onAlertClick}
          loading={loading}
        />
      )}

      {/* Rules View */}
      {view === 'rules' && (
        <RulesView 
          rules={rules}
          onDelete={handleDeleteRule}
          onToggle={handleToggleRule}
        />
      )}

      {/* New Rule Form */}
      {showNewRuleForm && (
        <NewAlertRuleForm 
          portfolioId={portfolio_id}
          onClose={() => setShowNewRuleForm(false)}
          onRuleCreated={() => {
            setShowNewRuleForm(false);
            fetchRules();
          }}
        />
      )}
    </div>
  );
};

interface AlertsViewProps {
  alerts: Alert[];
  filter: string;
  onFilterChange: (filter: 'all' | 'unacknowledged' | 'critical') => void;
  onAcknowledge: (alertId: string) => void;
  onAlertClick?: (alert: Alert) => void;
  loading: boolean;
}

const AlertsView: React.FC<AlertsViewProps> = ({
  alerts,
  filter,
  onFilterChange,
  onAcknowledge,
  onAlertClick,
  loading
}) => {
  return (
    <div className="space-y-4">
      {/* Filter Buttons */}
      <div className="flex gap-2">
        {(['all', 'unacknowledged', 'critical'] as const).map((f) => (
          <button
            key={f}
            onClick={() => onFilterChange(f)}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">
          <div className="animate-spin w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full mx-auto mb-4" />
          Loading alerts...
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
          <p className="text-gray-600 font-semibold">No {filter} alerts</p>
          <p className="text-sm text-gray-500">Great! Your portfolio is all clear</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onAcknowledge={() => onAcknowledge(alert.id)}
              onClick={() => onAlertClick?.(alert)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface AlertCardProps {
  alert: Alert;
  onAcknowledge: () => void;
  onClick?: () => void;
}

const AlertCard: React.FC<AlertCardProps> = ({ alert, onAcknowledge, onClick }) => {
  const severityConfig = {
    'INFO': { bg: 'bg-blue-50', border: 'border-blue-200', icon: Info, text: 'text-blue-600' },
    'WARNING': { bg: 'bg-yellow-50', border: 'border-yellow-200', icon: AlertCircle, text: 'text-yellow-600' },
    'CRITICAL': { bg: 'bg-red-50', border: 'border-red-200', icon: AlertTriangle, text: 'text-red-600' }
  };

  const config = severityConfig[alert.severity];
  const SeverityIcon = config.icon;

  return (
    <div
      onClick={onClick}
      className={`${config.bg} border-l-4 ${config.border} rounded-lg p-4 cursor-pointer hover:shadow-md transition`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3 flex-1">
          <SeverityIcon className={`w-5 h-5 ${config.text} flex-shrink-0 mt-0.5`} />
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">{alert.title}</h3>
            <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
            <div className="flex items-center gap-4 mt-2">
              <p className="text-xs text-gray-500">
                {new Date(alert.triggered_at).toLocaleString()}
              </p>
              {alert.metadata?.symbol && (
                <p className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                  {alert.metadata.symbol}
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 ml-4">
          {!alert.acknowledged ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onAcknowledge();
              }}
              className="px-3 py-1 text-sm bg-white rounded-lg text-gray-700 border border-gray-300 hover:bg-gray-100 transition"
            >
              Acknowledge
            </button>
          ) : (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              Acknowledged
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

interface RulesViewProps {
  rules: AlertRule[];
  onDelete: (ruleId: string) => void;
  onToggle: (ruleId: string, enabled: boolean) => void;
}

const RulesView: React.FC<RulesViewProps> = ({ rules, onDelete, onToggle }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {rules.length === 0 ? (
        <div className="col-span-full bg-white rounded-lg shadow-md p-8 text-center">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 font-semibold">No alert rules</p>
          <p className="text-sm text-gray-500">Create your first alert rule to get started</p>
        </div>
      ) : (
        rules.map((rule) => (
          <div key={rule.id} className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold text-gray-900">{rule.alert_type}</h3>
              <button
                onClick={() => onDelete(rule.id)}
                className="text-red-500 hover:text-red-700 transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 mb-4">
              <p className="text-xs text-gray-500">
                Created: {new Date(rule.created_at).toLocaleDateString()}
              </p>
              <p className="text-xs text-gray-500">
                Triggered: {rule.trigger_count} times
              </p>
              {rule.last_triggered && (
                <p className="text-xs text-gray-500">
                  Last: {new Date(rule.last_triggered).toLocaleDateString()}
                </p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-1 rounded ${
                rule.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                rule.severity === 'WARNING' ? 'bg-yellow-100 text-yellow-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {rule.severity}
              </span>
              <label className="ml-auto flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rule.enabled}
                  onChange={() => onToggle(rule.id, rule.enabled)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-xs text-gray-600">
                  {rule.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </label>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

interface NewAlertRuleFormProps {
  portfolioId: string;
  onClose: () => void;
  onRuleCreated: () => void;
}

const NewAlertRuleForm: React.FC<NewAlertRuleFormProps> = ({ portfolioId, onClose, onRuleCreated }) => {
  const [alertType, setAlertType] = useState('PRICE_TARGET');
  const [severity, setSeverity] = useState<'INFO' | 'WARNING' | 'CRITICAL'>('WARNING');
  const [symbol, setSymbol] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      await axios.post('/api/alerts/rules', {
        alert_type: alertType,
        portfolio_id: portfolioId,
        parameters: {
          symbol: symbol,
          target_price: parseFloat(targetPrice)
        },
        notification_channels: ['PUSH', 'EMAIL'],
        severity: severity,
        enabled: true
      });
      
      onRuleCreated();
    } catch (error) {
      console.error('Failed to create alert rule:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">New Alert Rule</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Alert Type</label>
            <select
              value={alertType}
              onChange={(e) => setAlertType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="PRICE_TARGET">Price Target</option>
              <option value="LOSS_THRESHOLD">Loss Threshold</option>
              <option value="GAIN_TARGET">Gain Target</option>
              <option value="VOLATILITY">Volatility Spike</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="e.g., AAPL"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Target Price</label>
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="e.g., 150.00"
              step="0.01"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>

          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AlertsDashboard;
