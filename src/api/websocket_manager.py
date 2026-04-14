"""WebSocket connection manager for real-time market data."""
from typing import List, Dict, Any
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts market data updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, set] = {}  # Track which symbols each client is subscribed to

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connected clients."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    async def broadcast_to_subscribers(self, symbol: str, data: Dict[str, Any]) -> None:
        """Broadcast market data only to clients subscribed to that symbol."""
        disconnected = []
        broadcast_count = 0
        
        for connection in self.active_connections:
            subscribed_symbols = self.subscriptions.get(connection, set())
            
            # Send if client subscribed to this symbol or subscribed to all (empty set means all)
            if not subscribed_symbols or symbol in subscribed_symbols:
                try:
                    message = {
                        "type": "market_update",
                        "symbol": symbol,
                        "data": data,
                    }
                    await connection.send_json(message)
                    broadcast_count += 1
                    logger.info(f"Broadcast {symbol} to 1 client (total: {broadcast_count})")
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    disconnected.append(connection)
        
        logger.info(f"Broadcast complete for {symbol}. Sent to {broadcast_count} clients")
        
        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    async def subscribe(self, websocket: WebSocket, symbol: str) -> None:
        """Subscribe a client to a symbol."""
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        
        self.subscriptions[websocket].add(symbol.upper())
        logger.info(f"Client subscribed to {symbol}. Subscriptions: {self.subscriptions[websocket]}")

    async def unsubscribe(self, websocket: WebSocket, symbol: str) -> None:
        """Unsubscribe a client from a symbol."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(symbol.upper())
            logger.info(f"Client unsubscribed from {symbol}. Subscriptions: {self.subscriptions[websocket]}")

    async def subscribe_all(self, websocket: WebSocket, symbols: List[str]) -> None:
        """Subscribe a client to multiple symbols at once."""
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        
        for symbol in symbols:
            self.subscriptions[websocket].add(symbol.upper())
        
        logger.info(f"Client subscribed to {len(symbols)} symbols. Subscriptions: {self.subscriptions[websocket]}")

    def get_active_connections_count(self) -> int:
        """Get the number of active WebSocket connections."""
        return len(self.active_connections)

    def get_all_subscribed_symbols(self) -> set:
        """Get all symbols that at least one client is subscribed to."""
        all_symbols = set()
        for symbols in self.subscriptions.values():
            all_symbols.update(symbols)
        return all_symbols


# Global instance
manager = ConnectionManager()
