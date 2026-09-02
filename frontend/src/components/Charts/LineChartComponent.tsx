import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface HoldingData {
  symbol: string
  quantity: number
  currentPrice: number
}

interface LineChartProps {
  holdings: HoldingData[]
}

// 1. Define the shape of each chart point
interface ChartPoint {
  date: string
  value: number
}

// 2. Explicitly type the return value of generateMockHistory
function generateMockHistory(holdings: HoldingData[]): ChartPoint[] {
  const currentTotal = holdings.reduce((sum, h) => sum + (h.quantity * h.currentPrice), 0)
  const data: ChartPoint[] = []
  
  for (let i = 29; i >= 0; i--) {
    const daysAgo = i
    const date = new Date()
    date.setDate(date.getDate() - daysAgo)
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    
    // Simulate value with small random fluctuations
    const volatilityFactor = 0.05 // 5% daily volatility
    const randomWalk = (Math.random() - 0.5) * 2 * volatilityFactor
    const historicalValue = currentTotal * (1 + randomWalk * (30 - i) / 30)
    
    data.push({
      date: dateStr,
      value: parseFloat(historicalValue.toFixed(2)),
    })
  }
  
  return data
}

export default function LineChartComponent({ holdings }: LineChartProps) {
  const chartData: ChartPoint[] = generateMockHistory(holdings)

  if (holdings.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <p>No holdings to display</p>
      </div>
    )
  }

  const currentValue = chartData[chartData.length - 1]?.value || 0
  const previousValue = chartData[0]?.value || 0
  const change = currentValue - previousValue
  const changePercent = previousValue !== 0 ? (change / previousValue) * 100 : 0

  return (
    <div className="w-full h-96 bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Portfolio Value (30 Days)
          </h3>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              ${currentValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className={`text-sm font-medium ${change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {change >= 0 ? '↑' : '↓'} ${Math.abs(change).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({changePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '12px' }} />
          <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
          <Tooltip 
            formatter={(value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            contentStyle={{ 
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#0ea5e9" 
            dot={false}
            strokeWidth={2}
            isAnimationActive={true}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}