import { Trash2, Edit2 } from 'lucide-react'

export interface Holding {
  symbol: string
  quantity: number
  costBasis?: number
  currentPrice: number
}

interface HoldingsTableProps {
  holdings: Holding[]
  onEdit?: (symbol: string) => void
  onDelete?: (symbol: string) => void
  isLoading?: boolean
}

export default function HoldingsTable({
  holdings,
  onEdit,
  onDelete,
  isLoading = false,
}: HoldingsTableProps) {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        </div>
      </div>
    )
  }

  if (holdings.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center h-64 text-gray-500">
          <p>No holdings yet. Add one to get started!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Price
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Value
              </th>
              {holdings.some(h => h.costBasis) && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Gain/Loss
                </th>
              )}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding) => {
              const value = holding.quantity * holding.currentPrice
              const costTotal = (holding.costBasis || 0) * holding.quantity
              const gain = value - costTotal
              const gainPercent = costTotal > 0 ? (gain / costTotal) * 100 : 0

              return (
                <tr
                  key={holding.symbol}
                  className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {holding.symbol}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {holding.quantity}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      ${holding.currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      ${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </td>
                  {holdings.some(h => h.costBasis) && (
                    <td className="px-6 py-4 whitespace-nowrap">
                      {holding.costBasis && (
                        <span className={`text-sm font-medium ${gain >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                          {gain >= 0 ? '+' : ''}{gain.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({gainPercent.toFixed(1)}%)
                        </span>
                      )}
                    </td>
                  )}
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center gap-2">
                      {onEdit && (
                        <button
                          onClick={() => onEdit(holding.symbol)}
                          className="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-blue-100 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                          title="Edit holding"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                      )}
                      {onDelete && (
                        <button
                          onClick={() => onDelete(holding.symbol)}
                          className="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          title="Delete holding"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
