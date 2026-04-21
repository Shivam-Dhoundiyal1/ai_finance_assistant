import { TrendingUp, TrendingDown, PieChart } from 'lucide-react';

interface MetricsData {
  totalValue: number
  totalReturn: number
  returnPercent: number
  allocationScore: number
  riskScore: number
}

interface MetricsCardsProps {
  metrics: MetricsData
}

export default function MetricsCards({ metrics }: MetricsCardsProps) {
  const isPositive = metrics.totalReturn >= 0

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {/* Total Value Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Value</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">
              ${metrics.totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>
          <PieChart className="w-8 h-8 text-blue-500" />
        </div>
      </div>

      {/* Total Return Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Return</p>
            <p className={`text-2xl font-bold mt-2 ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {isPositive ? '+' : ''}{metrics.totalReturn.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
            <p className={`text-xs font-medium mt-1 ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {isPositive ? '+' : ''}{metrics.returnPercent.toFixed(2)}%
            </p>
          </div>
          {isPositive ? (
            <TrendingUp className="w-8 h-8 text-green-500" />
          ) : (
            <TrendingDown className="w-8 h-8 text-red-500" />
          )}
        </div>
      </div>

      {/* Allocation Score Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Allocation Score</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">
              {metrics.allocationScore}%
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {metrics.allocationScore >= 75 ? 'Excellent' : metrics.allocationScore >= 50 ? 'Good' : 'Fair'}
            </p>
          </div>
          <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <span className="text-blue-600 dark:text-blue-400 font-semibold">⚖️</span>
          </div>
        </div>
      </div>

      {/* Risk Score Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Risk Score</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">
              {metrics.riskScore}%
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {metrics.riskScore >= 70 ? 'High' : metrics.riskScore >= 40 ? 'Medium' : 'Low'}
            </p>
          </div>
          <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <span className="text-amber-600 dark:text-amber-400 font-semibold">⚠️</span>
          </div>
        </div>
      </div>

      {/* Holdings Count Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Diversification</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">
              Well
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Multiple sectors
            </p>
          </div>
          <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <span className="text-green-600 dark:text-green-400 font-semibold">✓</span>
          </div>
        </div>
      </div>
    </div>
  )
}
