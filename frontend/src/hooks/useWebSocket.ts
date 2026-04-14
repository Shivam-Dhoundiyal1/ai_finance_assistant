import { useEffect, useRef, useState, useCallback } from 'react';

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface MarketUpdate {
  type: 'market_update';
  symbol: string;
  data: {
    price: number;
    change: number;
    change_percent: number;
    timestamp: string;
  };
}

export interface UseWebSocketOptions {
  url?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    url = 'ws://localhost:8000/api/v1/ws/market',
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const ws = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<MarketUpdate | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const subscribedSymbols = useRef<Set<string>>(new Set());

  const connect = useCallback(async () => {
    if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    try {
      setStatus('connecting');
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('[WebSocket] Connected to market data');
        setStatus('connected');
        reconnectAttempts.current = 0;

        // Resubscribe to symbols after reconnection
        if (subscribedSymbols.current.size > 0) {
          const symbols = Array.from(subscribedSymbols.current);
          subscribe(symbols);
        }
      };

      ws.current.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data) as MarketUpdate;
          if (data.type === 'market_update') {
            setLastMessage(data);
          }
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      ws.current.onerror = (error: Event) => {
        console.error('[WebSocket] Error:', error);
        setStatus('error');
      };

      ws.current.onclose = () => {
        console.log('[WebSocket] Connection closed');
        setStatus('disconnected');

        // Attempt to reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current += 1;
          console.log(`[WebSocket] Reconnecting... (attempt ${reconnectAttempts.current}/${maxReconnectAttempts})`);
          reconnectTimeout.current = setTimeout(connect, reconnectInterval);
        }
      };
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
      setStatus('error');
    }
  }, [url, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    subscribedSymbols.current.clear();
    setStatus('disconnected');
  }, []);

  const subscribe = useCallback((symbols: string[]) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Cannot subscribe: WebSocket not connected');
      return;
    }

    const upperSymbols = symbols.map((s) => s.toUpperCase());
    upperSymbols.forEach((s) => subscribedSymbols.current.add(s));

    try {
      ws.current.send(
        JSON.stringify({
          type: 'subscribe',
          symbols: upperSymbols,
        })
      );
      console.log('[WebSocket] Subscribed to:', upperSymbols);
    } catch (error) {
      console.error('[WebSocket] Failed to send subscribe message:', error);
    }
  }, []);

  const unsubscribe = useCallback((symbols: string[]) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.warn('[WebSocket] Cannot unsubscribe: WebSocket not connected');
      return;
    }

    const upperSymbols = symbols.map((s) => s.toUpperCase());
    upperSymbols.forEach((s) => subscribedSymbols.current.delete(s));

    try {
      ws.current.send(
        JSON.stringify({
          type: 'unsubscribe',
          symbols: upperSymbols,
        })
      );
      console.log('[WebSocket] Unsubscribed from:', upperSymbols);
    } catch (error) {
      console.error('[WebSocket] Failed to send unsubscribe message:', error);
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    status,
    lastMessage,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    isConnected: status === 'connected',
    isConnecting: status === 'connecting',
  };
}
