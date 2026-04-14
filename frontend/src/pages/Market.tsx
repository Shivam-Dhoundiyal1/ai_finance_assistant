import { useState, useEffect } from 'react'
import { apiService, type QuoteResponse } from '../api'
import { useWebSocket } from '../hooks/useWebSocket'
import { ConnectionStatusIndicator } from '../components/Market/ConnectionStatus'
import { TrendingUp, TrendingDown, RefreshCw, Search } from 'lucide-react'

export default function Market() {
  const [quotes, setQuotes] = useState<Record<string, QuoteResponse>>({})
  const [symbols, setSymbols] = useState(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [searchSymbol, setSearchSymbol] = useState('')
  const [fallbackMode, setFallbackMode] = useState(false)

  const { status, isConnected, subscribe, unsubscribe, lastMessage } = useWebSocket({
    autoConnect: true,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
  })

  // Fetch initial quotes via HTTP (if WebSocket not available)
  useEffect(() => {
    const fetchInitialQuotes = async () => {
      try {
        const newQuotes: Record<string, QuoteResponse> = {}
        for (const symbol of symbols) {
          const quote = await apiService.getQuote(symbol)
          newQuotes[symbol] = quote
        }
        setQuotes(newQuotes)
        setLastUpdate(new Date())
      } catch (err) {
        console.error('Failed to load quotes:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchInitialQuotes()
  }, [])

  // Subscribe to symbols when WebSocket connects
  useEffect(() => {
    if (isConnected && symbols.length > 0) {
      subscribe(symbols)
      console.log('Subscribed to symbols:', symbols)
    }
  }, [isConnected, symbols, subscribe])

  // Update quotes when WebSocket message arrives
  useEffect(() => {
    if (lastMessage?.type === 'market_update') {
      const { symbol, data } = lastMessage
      setQuotes((prev) => ({
        ...prev,
        [symbol]: {
          symbol,
          price: data.price,
          change: data.change,
          change_percent: data.change_percent,
          currency: 'USD',
        },
      }))
      setLastUpdate(new Date())
    }
  }, [lastMessage])

  // Fallback to HTTP polling if WebSocket fails
  useEffect(() => {
    if (status === 'error' || status === 'disconnected') {
      if (!fallbackMode) {
        console.log('WebSocket unavailable, falling back to HTTP polling')
        setFallbackMode(true)
      }

      const interval = setInterval(async () => {
        try {
          const newQuotes: Record<string, QuoteResponse> = {}
          for (const symbol of symbols) {
            const quote = await apiService.getQuote(symbol)
            newQuotes[symbol] = quote
          }
          setQuotes(newQuotes)
          setLastUpdate(new Date())
        } catch (err) {
          console.error('Failed to load quotes:', err)
        }
      }, 5000)

      return () => clearInterval(interval)
    }
  }, [status, fallbackMode, symbols])

  const handleSearch = async () => {
    if (!searchSymbol.trim()) return

    const upperSymbol = searchSymbol.toUpperCase()

    // Try to fetch quote
    try {
      const quote = await apiService.getQuote(upperSymbol)
      setQuotes((prev) => ({ ...prev, [upperSymbol]: quote }))

      // Subscribe if WebSocket is connected
      if (isConnected) {
        subscribe([upperSymbol])
      }

      // Add to symbols list if not already there
      if (!symbols.includes(upperSymbol)) {
        setSymbols((prev) => [...prev, upperSymbol])
      }

      setSearchSymbol('')
    } catch (err) {
      console.error('Failed to fetch quote:', err)
    }
  }

  const handleRemoveSymbol = (symbol: string) => {
    setSymbols((prev) => prev.filter((s) => s !== symbol))
    if (isConnected) {
      unsubscribe([symbol])
    }
    setQuotes((prev) => {
      const newQuotes = { ...prev }
      delete newQuotes[symbol]
      return newQuotes
    })
  }

  const loadQuotesManually = async () => {
    setLoading(true)
    try {
      const newQuotes: Record<string, QuoteResponse> = {}
      for (const symbol of symbols) {
        const quote = await apiService.getQuote(symbol)
        newQuotes[symbol] = quote
      }
      setQuotes(newQuotes)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('Failed to load quotes:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-gray-100">
            Market Overview
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mt-2">
            Real-time market data and quotes
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <ConnectionStatusIndicator status={status} showLabel={true} />
        </div>
      </div>

      {/* Search Bar */}
      <div className="card">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search stock symbol..."
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="input flex-1"
          />
          <button onClick={handleSearch} className="btn btn-primary">
            <Search className="w-5 h-5" />
          </button>
        </div>
        {fallbackMode && (
          <p className="mt-2 text-sm text-yellow-600 dark:text-yellow-400">
            ⚠️ Real-time updates unavailable. Using polling mode.
          </p>
        )}
      </div>

      {/* Market Status */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 card">
        <div className="text-center sm:text-left">
          <p className="text-sm text-gray-500 dark:text-gray-400">Last updated</p>
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <button 
          onClick={loadQuotesManually} 
          className="btn btn-secondary"
          disabled={loading}
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[...symbols, ...Object.keys(quotes).filter(s => !symbols.includes(s))].map(symbol => {
            const quote = quotes[symbol]
            if (!quote) return null

            return (
              <div key={symbol} className="market-card relative">
                <button
                  onClick={() => handleRemoveSymbol(symbol)}
                  className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-lg leading-none"
                  title="Remove from watchlist"
                >
                  ✕
                </button>

                <div className="flex items-center justify-between mb-3">
                  <h3 className="market-symbol">{symbol}</h3>
                  {quote.source && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {quote.source}
                    </span>
                  )}
                </div>
                
                <div className="market-price">
                  ${quote.price.toFixed(2)}
                </div>
                
                <div className={`flex items-center justify-center gap-1 mt-2 text-sm ${
                  quote.change >= 0 ? 'market-change-positive' : 'market-change-negative'
                }`}>
                  {quote.change >= 0 ? (
                    <TrendingUp className="w-4 h-4" />
                  ) : (
                    <TrendingDown className="w-4 h-4" />
                  )}
                  <span>
                    {quote.change >= 0 ? '+' : ''}{quote.change.toFixed(2)} ({quote.change_percent.toFixed(2)}%)
                  </span>
                </div>
                
                {quote.error && (
                  <div className="mt-2 text-xs text-red-600 dark:text-red-400">
                    {quote.error}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
