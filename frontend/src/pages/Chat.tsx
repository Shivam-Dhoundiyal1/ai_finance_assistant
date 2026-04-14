import { useState, useRef, useEffect } from 'react'
import { apiService, type ChatResponse } from '../api'
import { Send, Bot, User, Sparkles } from 'lucide-react'

type Message = {
  role: 'user' | 'assistant'
  content: string
  agent?: string
  sources?: string[]
  routing_confidence?: number
  success?: boolean
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    setError(null)

    try {
      const data: ChatResponse = await apiService.sendMessage(text)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          agent: data.agent,
          sources: data.sources ?? [],
          routing_confidence: data.routing_confidence,
          success: data.success,
        },
      ])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col flex-1 h-full">
      {/* Header */}
      <div className="text-center space-y-2 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 flex-shrink-0">
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-gray-100">
          Financial Assistant
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Ask about investing, portfolios, market data, goals, or taxes. 
          Responses are educational only.
        </p>
      </div>

      {/* Chat container */}
      <div className="flex-1 bg-white dark:bg-gray-800 rounded-t-xl shadow-lg border border-gray-200 dark:border-gray-700 border-b-0 overflow-hidden flex flex-col mx-4 sm:mx-6 lg:mx-8 mb-4">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Welcome to Finnie AI
                </h3>
                <p className="text-gray-600 dark:text-gray-400 max-w-md">
                  Send a message to start. Try: "What is diversification?" or "AAPL price"
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  "What is diversification?",
                  "AAPL stock price",
                  "Analyze my portfolio",
                  "Retirement planning tips"
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  
                  <div className={`max-w-2xl ${msg.role === 'user' ? 'order-first' : ''}`}>
                    <div className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      
                      {msg.role === 'assistant' && msg.agent && (
                        <div className="message-meta">
                          <span className="flex items-center gap-1">
                            <Sparkles className="w-4 h-4" />
                            {msg.agent}
                          </span>
                          {msg.routing_confidence && (
                            <span className="message-confidence">
                              {(msg.routing_confidence * 100).toFixed(0)}% confidence
                            </span>
                          )}
                        </div>
                      )}
                      
                      {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                          Sources: {msg.sources.slice(0, 3).join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="message message-assistant">
                    <div className="flex items-center gap-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-gray-500 dark:text-gray-400">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Error display */}
        {error && (
          <div className="mx-4 mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex-shrink-0">
            <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Input form */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={loading}
              className="input flex-1"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
