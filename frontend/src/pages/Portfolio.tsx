import { useState, useEffect } from 'react'
import { Plus, X } from 'lucide-react'
import { apiService, type PortfolioData, type Holding, type HoldingWithPrice } from '../api'
import PieChartComponent from '../components/Charts/PieChartComponent'
import BarChartComponent from '../components/Charts/BarChartComponent'
import LineChartComponent from '../components/Charts/LineChartComponent'
import MetricsCards from '../components/Portfolio/MetricsCards'
import HoldingsTable from '../components/Portfolio/HoldingsTable'

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newHolding, setNewHolding] = useState<Holding>({ symbol: '', quantity: 0, avg_cost: 0 })

  useEffect(() => {
    loadPortfolio()
  }, [])

  const loadPortfolio = async () => {
    try {
      setLoading(true)
      const data = await apiService.getPortfolio()
      setPortfolio(data)
    } catch (err) {
      console.error('Failed to load portfolio:', err)
    } finally {
      setLoading(false)
    }
  }

  const addHolding = async () => {
    if (!portfolio || !newHolding.symbol.trim()) return
    
    try {
      const updatedPortfolio = {
        ...portfolio,
        holdings: [...portfolio.holdings, { ...newHolding, symbol: newHolding.symbol.toUpperCase() }]
      }
      
      await apiService.savePortfolio(updatedPortfolio)
      setPortfolio(updatedPortfolio)
      setNewHolding({ symbol: '', quantity: 0, avg_cost: 0 })
      setShowAddForm(false)
    } catch (err) {
      console.error('Failed to add holding:', err)
    }
  }

  const removeHolding = async (symbol: string) => {
    if (!portfolio) return
    
    try {
      await apiService.deleteHolding(symbol)
      const updatedPortfolio = {
        ...portfolio,
        holdings: portfolio.holdings.filter(h => h.symbol !== symbol)
      }
      setPortfolio(updatedPortfolio)
    } catch (err) {
      console.error('Failed to delete holding:', err)
    }
  }

  const calculateMetrics = () => {
    if (!portfolio || portfolio.holdings.length === 0) {
      return {
        totalValue: 0,
        totalReturn: 0,
        returnPercent: 0,
        allocationScore: 0,
        riskScore: 0,
      }
    }

    // Get current holdings with market prices (mock for demo)
    const currentValue = portfolio.total_value || portfolio.holdings.reduce((sum, h) => sum + (h.quantity * h.avg_cost), 0)
    const costBasis = portfolio.holdings.reduce((sum, h) => sum + (h.quantity * h.avg_cost), 0)
    const totalReturn = currentValue - costBasis
    const returnPercent = costBasis > 0 ? (totalReturn / costBasis) * 100 : 0

    // Allocation score based on number of holdings
    const allocationScore = Math.min(100, portfolio.holdings.length * 20)
    
    // Risk score based on concentration
    const percentages = portfolio.holdings.map(h => (h.quantity * h.avg_cost) / currentValue)
    const maxConcentration = Math.max(...percentages, 0)
    const riskScore = Math.min(100, 30 + maxConcentration * 70)

    return {
      totalValue: currentValue,
      totalReturn,
      returnPercent,
      allocationScore,
      riskScore,
    }
  }

  const holdingsWithPrices: HoldingWithPrice[] = portfolio?.holdings.map(h => ({
    symbol: h.symbol,
    quantity: h.quantity,
    currentPrice: h.avg_cost,
    costBasis: h.avg_cost,
  })) || []

  const metrics = calculateMetrics()

  return (
    <div className="flex flex-col h-full space-y-6 px-4 sm:px-6 lg:px-8 py-6 overflow-auto">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-gray-100">
            Portfolio Dashboard
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mt-2">
            Manage your investments and track performance
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : portfolio ? (
        <div className="space-y-6">
          {/* Metrics Cards */}
          <MetricsCards metrics={metrics} />

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PieChartComponent holdings={holdingsWithPrices} />
            <BarChartComponent holdings={holdingsWithPrices} />
          </div>

          {/* Line Chart - Full Width */}
          <LineChartComponent holdings={holdingsWithPrices} />

          {/* Holdings Table */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Holdings</h2>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="btn btn-primary flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Add Holding
              </button>
            </div>

            <HoldingsTable
              holdings={holdingsWithPrices}
              onDelete={removeHolding}
              isLoading={loading}
            />

            {/* Add Holding Form */}
            {showAddForm && (
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Add New Holding
                  </h3>
                  <button
                    onClick={() => setShowAddForm(false)}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Symbol
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., AAPL"
                      className="input"
                      value={newHolding.symbol}
                      onChange={(e) =>
                        setNewHolding({
                          ...newHolding,
                          symbol: e.target.value.toUpperCase(),
                        })
                      }
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Quantity
                    </label>
                    <input
                      type="number"
                      placeholder="100"
                      className="input"
                      value={newHolding.quantity || ''}
                      onChange={(e) =>
                        setNewHolding({
                          ...newHolding,
                          quantity: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Avg Cost
                    </label>
                    <input
                      type="number"
                      placeholder="150.00"
                      step="0.01"
                      className="input"
                      value={newHolding.avg_cost || ''}
                      onChange={(e) =>
                        setNewHolding({
                          ...newHolding,
                          avg_cost: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </div>

                  <div className="flex items-end gap-2">
                    <button
                      onClick={addHolding}
                      className="btn btn-primary flex-1"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => setShowAddForm(false)}
                      className="btn btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center py-12 text-gray-500">
          <p>No portfolio data available</p>
        </div>
      )}
    </div>
  )
}
