import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from 'recharts'

interface HoldingData {
  symbol: string
  quantity: number
  currentPrice: number
}

interface PieChartProps {
  holdings: HoldingData[]
}

const COLORS = ['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#f59e0b', '#ef4444']

export default function PieChartComponent({ holdings }: PieChartProps) {
  // Calculate allocation data
  const allocationData = holdings.map((holding, idx) => {
    const value = holding.quantity * holding.currentPrice
    return {
      name: holding.symbol,
      value: parseFloat(value.toFixed(2)),
      color: COLORS[idx % COLORS.length],
    }
  })

  const totalValue = allocationData.reduce((sum, item) => sum + item.value, 0)

  if (allocationData.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <p>No holdings to display</p>
      </div>
    )
  }

  return (
    <div className="w-full h-96 bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Portfolio Allocation
      </h3>
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={allocationData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {allocationData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            contentStyle={{ 
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff'
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p>Total Portfolio Value: <span className="font-semibold text-gray-900 dark:text-gray-100">${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span></p>
      </div>
    </div>
  )
}
