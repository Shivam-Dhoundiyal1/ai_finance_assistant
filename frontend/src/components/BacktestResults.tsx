import React, { useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

interface BacktestResult {
  portfolio_name: string;
  start_date: string;
  end_date: string;
  initial_investment: number;
  final_value: number;
  total_return: number;
  total_return_pct: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  max_drawdown_duration: number;
  vs_sp500_return?: number;
  vs_sp500_outperformance?: number;
  positive_months: number;
  negative_months: number;
  best_month?: number;
  worst_month?: number;
  value_history?: Array<[string, number]>;
  monthly_returns?: number[];
}

interface BacktestResultsProps {
  results: BacktestResult[];
  selectedIndex?: number;
  onSelectResult?: (index: number) => void;
}

/**
 * Backtest Results Component
 *
 * Displays comprehensive backtesting results including:
 * - Portfolio performance metrics
 * - Risk analysis (volatility, max drawdown, Sharpe ratio)
 * - Growth chart and equity curve
 * - Monthly returns distribution
 * - Benchmark comparison
 */
export const BacktestResults: React.FC<BacktestResultsProps> = ({
  results,
  selectedIndex = 0,
  onSelectResult
}) => {
  const [view, setView] = useState<'overview' | 'details' | 'comparison'>('overview');
  const selectedResult = results[selectedIndex] || results[0];

  if (!selectedResult || results.length === 0) {
    return (
      <div className="w-full bg-gray-50 rounded-lg p-8 text-center">
        <AlertCircle className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <p className="text-gray-600 font-semibold">No backtest results available</p>
        <p className="text-sm text-gray-500">Run a backtest to see historical performance</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header & View Selector */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{selectedResult.portfolio_name}</h2>
            <p className="text-sm text-gray-600">
              {new Date(selectedResult.start_date).toLocaleDateString()} - {new Date(selectedResult.end_date).toLocaleDateString()}
            </p>
          </div>
          <div className="text-right">
            <p className="text-4xl font-bold text-green-600">{selectedResult.total_return_pct.toFixed(2)}%</p>
            <p className="text-sm text-gray-600">Total Return</p>
          </div>
        </div>

        {/* View Tabs */}
        <div className="flex gap-2 border-b border-gray-200">
          {(['overview', 'details', 'comparison'] as const).map((v) => (
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

      {/* Overview Tab */}
      {view === 'overview' && (
        <OverviewTab result={selectedResult} />
      )}

      {/* Details Tab */}
      {view === 'details' && (
        <DetailsTab result={selectedResult} />
      )}

      {/* Comparison Tab */}
      {view === 'comparison' && results.length > 1 && (
        <ComparisonTab results={results} selectedIndex={selectedIndex} onSelectResult={onSelectResult} />
      )}

      {/* Strategy Selector */}
      {results.length > 1 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Strategy</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((result, index) => (
              <button
                key={index}
                onClick={() => onSelectResult?.(index)}
                className={`p-4 rounded-lg border-2 transition ${
                  index === selectedIndex
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <p className="font-semibold text-gray-900">{result.portfolio_name}</p>
                <p className="text-sm text-gray-600 mt-1">
                  Return: <span className="font-bold text-green-600">{result.total_return_pct.toFixed(2)}%</span>
                </p>
                <p className="text-sm text-gray-600">
                  Annualized: <span className="font-bold">{result.annualized_return.toFixed(2)}%</span>
                </p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

interface OverviewTabProps {
  result: BacktestResult;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ result }) => {
  // Generate value history data for chart
  const valueHistoryData = result.value_history?.map(([date, value]) => ({
    date: new Date(date).toLocaleDateString(),
    value: Math.round(value)
  })) || [];

  return (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Final Value"
          value={`$${result.final_value.toLocaleString('en-US', {maximumFractionDigits: 0})}`}
          change={result.total_return}
          positive={result.total_return >= 0}
        />
        <MetricCard
          label="Annualized Return"
          value={`${result.annualized_return.toFixed(2)}%`}
          positive={result.annualized_return >= 0}
        />
        <MetricCard
          label="Volatility"
          value={`${result.volatility.toFixed(2)}%`}
          subtitle="Annual volatility (risk)"
        />
        <MetricCard
          label="Sharpe Ratio"
          value={result.sharpe_ratio.toFixed(2)}
          subtitle="Risk-adjusted return"
        />
      </div>

      {/* Growth Chart */}
      {valueHistoryData.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Value Over Time</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={valueHistoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip 
                formatter={(value) => `$${(value as number).toLocaleString()}`}
                labelStyle={{ color: '#000' }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Benchmark Comparison */}
      {result.vs_sp500_return !== undefined && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">vs Benchmark (S&P 500)</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">Portfolio Return</p>
              <p className="text-2xl font-bold text-blue-600">{result.total_return_pct.toFixed(2)}%</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">S&P 500 Return</p>
              <p className="text-2xl font-bold text-gray-600">{result.vs_sp500_return.toFixed(2)}%</p>
            </div>
            <div className={`rounded-lg p-4 ${result.vs_sp500_outperformance! >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
              <p className="text-sm text-gray-600">Outperformance</p>
              <p className={`text-2xl font-bold ${result.vs_sp500_outperformance! >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {result.vs_sp500_outperformance?.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface DetailsTabProps {
  result: BacktestResult;
}

const DetailsTab: React.FC<DetailsTabProps> = ({ result }) => {
  const monthlyData = result.monthly_returns?.map((ret, idx) => ({
    month: `Month ${idx + 1}`,
    return: ret
  })) || [];

  const winRate = result.positive_months + result.negative_months > 0 
    ? (result.positive_months / (result.positive_months + result.negative_months)) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Metrics</h3>
          <div className="space-y-4">
            <RiskMetricRow 
              label="Max Drawdown" 
              value={`-${result.max_drawdown.toFixed(2)}%`}
              subtitle={`Duration: ${result.max_drawdown_duration} days`}
              negative
            />
            <RiskMetricRow 
              label="Volatility" 
              value={`${result.volatility.toFixed(2)}%`}
              subtitle="Annual volatility"
            />
            <RiskMetricRow 
              label="Sharpe Ratio" 
              value={result.sharpe_ratio.toFixed(2)}
              subtitle="Risk-adjusted return"
            />
            <RiskMetricRow 
              label="Sortino Ratio" 
              value={result.sortino_ratio.toFixed(2)}
              subtitle="Downside risk ratio"
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Performance</h3>
          <div className="space-y-3">
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm text-gray-600">Positive Months</p>
              <p className="text-2xl font-bold text-green-600">{result.positive_months}</p>
              <p className="text-xs text-gray-500 mt-1">Win Rate: {winRate.toFixed(1)}%</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <p className="text-sm text-gray-600">Negative Months</p>
              <p className="text-2xl font-bold text-red-600">{result.negative_months}</p>
            </div>
            {result.best_month !== undefined && (
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600">Best Month</p>
                <p className="text-lg font-bold text-blue-600">+{result.best_month.toFixed(2)}%</p>
              </div>
            )}
            {result.worst_month !== undefined && (
              <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <p className="text-sm text-gray-600">Worst Month</p>
                <p className="text-lg font-bold text-yellow-600">{result.worst_month.toFixed(2)}%</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Monthly Returns Chart */}
      {monthlyData.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Returns Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value) => `${(value as number).toFixed(2)}%`}
                labelStyle={{ color: '#000' }}
              />
              <Bar 
                dataKey="return" 
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Summary Table */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <DetailRow label="Initial Investment" value={`$${result.initial_investment.toLocaleString()}`} />
          <DetailRow label="Final Value" value={`$${result.final_value.toLocaleString('en-US', {maximumFractionDigits: 0})}`} />
          <DetailRow label="Total Return" value={`$${result.total_return.toLocaleString('en-US', {maximumFractionDigits: 0})}`} />
          <DetailRow label="Total Return %" value={`${result.total_return_pct.toFixed(2)}%`} />
          <DetailRow label="Annualized Return" value={`${result.annualized_return.toFixed(2)}%`} />
          <DetailRow label="Period" value={`${result.max_drawdown_duration} days`} />
        </div>
      </div>
    </div>
  );
};

interface ComparisonTabProps {
  results: BacktestResult[];
  selectedIndex: number;
  onSelectResult?: (index: number) => void;
}

const ComparisonTab: React.FC<ComparisonTabProps> = ({ results, selectedIndex, onSelectResult }) => {
  const comparisonData = results.map((result, idx) => ({
    name: result.portfolio_name,
    annualizedReturn: result.annualized_return,
    volatility: result.volatility,
    sharpe: result.sharpe_ratio,
    maxDrawdown: Math.abs(result.max_drawdown),
    idx
  }));

  return (
    <div className="space-y-6">
      {/* Risk vs Return Scatter */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk vs Return</h3>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="volatility" 
              name="Volatility (%)"
              label={{ value: 'Volatility (%)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              dataKey="annualizedReturn" 
              name="Return (%)"
              label={{ value: 'Return (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null;
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-2 border border-gray-300 rounded shadow">
                    <p className="font-semibold text-gray-900">{data.name}</p>
                    <p className="text-sm">Return: {data.annualizedReturn.toFixed(2)}%</p>
                    <p className="text-sm">Volatility: {data.volatility.toFixed(2)}%</p>
                  </div>
                );
              }}
            />
            <Scatter 
              name="Portfolios"
              data={comparisonData}
              fill="#3b82f6"
              onClick={(data) => onSelectResult?.(data.idx)}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Comparison Table */}
      <div className="bg-white rounded-lg shadow-md p-6 overflow-x-auto">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Strategy Comparison</h3>
        <table className="w-full text-sm">
          <thead className="border-b-2 border-gray-300">
            <tr>
              <th className="text-left py-2 px-4 font-semibold text-gray-900">Strategy</th>
              <th className="text-right py-2 px-4 font-semibold text-gray-900">Return</th>
              <th className="text-right py-2 px-4 font-semibold text-gray-900">Ann. Return</th>
              <th className="text-right py-2 px-4 font-semibold text-gray-900">Volatility</th>
              <th className="text-right py-2 px-4 font-semibold text-gray-900">Sharpe</th>
              <th className="text-right py-2 px-4 font-semibold text-gray-900">Max DD</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, idx) => (
              <tr 
                key={idx}
                onClick={() => onSelectResult?.(idx)}
                className={`border-b border-gray-200 cursor-pointer ${
                  idx === selectedIndex ? 'bg-blue-50' : 'hover:bg-gray-50'
                }`}
              >
                <td className="py-3 px-4 font-semibold text-gray-900">{result.portfolio_name}</td>
                <td className="text-right py-3 px-4 text-green-600 font-semibold">{result.total_return_pct.toFixed(2)}%</td>
                <td className="text-right py-3 px-4 text-blue-600 font-semibold">{result.annualized_return.toFixed(2)}%</td>
                <td className="text-right py-3 px-4 text-gray-600">{result.volatility.toFixed(2)}%</td>
                <td className="text-right py-3 px-4 text-gray-600">{result.sharpe_ratio.toFixed(2)}</td>
                <td className="text-right py-3 px-4 text-red-600 font-semibold">-{result.max_drawdown.toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ===== Utility Components =====

interface MetricCardProps {
  label: string;
  value: string;
  change?: number;
  positive?: boolean;
  subtitle?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, change, positive, subtitle }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      {change !== undefined && (
        <div className="flex items-center gap-1 mt-2">
          {positive ? (
            <TrendingUp className="w-4 h-4 text-green-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
          <p className={`text-sm font-semibold ${positive ? 'text-green-600' : 'text-red-600'}`}>
            ${Math.abs(change).toLocaleString('en-US', {maximumFractionDigits: 0})}
          </p>
        </div>
      )}
    </div>
  );
};

interface RiskMetricRowProps {
  label: string;
  value: string;
  subtitle?: string;
  negative?: boolean;
}

const RiskMetricRow: React.FC<RiskMetricRowProps> = ({ label, value, subtitle, negative }) => {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div>
        <p className="text-sm font-semibold text-gray-900">{label}</p>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
      <p className={`text-lg font-bold ${negative ? 'text-red-600' : 'text-gray-900'}`}>{value}</p>
    </div>
  );
};

interface DetailRowProps {
  label: string;
  value: string;
}

const DetailRow: React.FC<DetailRowProps> = ({ label, value }) => {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-200">
      <p className="text-gray-600">{label}</p>
      <p className="font-semibold text-gray-900">{value}</p>
    </div>
  );
};

export default BacktestResults;
