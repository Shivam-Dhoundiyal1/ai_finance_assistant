import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

interface HoldingData {
  symbol: string
  quantity: number
  currentPrice: number
}

interface BarChartProps {
  holdings: HoldingData[]
}

// Simple sector mapping for demo purposes
const SECTOR_MAP: Record<string, string> = {
  'AAPL': 'Technology',
  'GOOGL': 'Technology',
  'MSFT': 'Technology',
  'AMZN': 'Consumer',
  'JPM': 'Finance',
  'BAC': 'Finance',
  'JNJ': 'Healthcare',
  'PG': 'Consumer',
  'XOM': 'Energy',
  'CVX': 'Energy',
  'TSM': 'Technology',
  'NVDA': 'Technology',
  'META': 'Technology',
  'NFLX': 'Technology',
}

export default function BarChartComponent({ holdings }: BarChartProps) {
  // Group by sector
  const sectorData: Record<string, number> = {}
  
  holdings.forEach((holding) => {
    const sector = SECTOR_MAP[holding.symbol] || 'Other'
    const value = holding.quantity * holding.currentPrice
    
    if (!sectorData[sector]) {
      sectorData[sector] = 0
    }
    sectorData[sector] += value
  })

  // Convert to chart data
  const chartData = Object.entries(sectorData).map(([sector, value]) => ({
    name: sector,
    value: parseFloat(value.toFixed(2)),
  }))

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <p>No holdings to display</p>
      </div>
    )
  }

  const COLORS = ['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#f59e0b', '#ef4444']

  return (
    <div className="w-full h-96 bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Sector Breakdown
      </h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip 
            formatter={(value: number) => `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            contentStyle={{ 
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#ffffff'
            }}
          />
          <Bar dataKey="value" fill="#0ea5e9" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
