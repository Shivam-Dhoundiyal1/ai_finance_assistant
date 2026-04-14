"""Background tasks for fetching and broadcasting market data."""
import asyncio
import logging
from datetime import datetime

from src.data.market_service import get_real_time_quote
from src.api.websocket_manager import manager

logger = logging.getLogger(__name__)

# Store the background task reference
quote_fetcher_task = None
FETCH_INTERVAL = 5  # seconds - reduced for faster testing/feedback


async def fetch_and_broadcast_quotes() -> None:
    """
    Background task that fetches market quotes and broadcasts them to all connected clients.
    Runs continuously, fetching quotes at regular intervals for subscribed symbols.
    """
    global quote_fetcher_task
    
    while True:
        try:
            # Get all symbols that clients are subscribed to
            symbols_to_fetch = manager.get_all_subscribed_symbols()
            logger.info(f"Background task check - subscribed symbols: {symbols_to_fetch}, active connections: {manager.get_active_connections_count()}")
            
            if not symbols_to_fetch:
                # No active subscriptions, just wait
                await asyncio.sleep(FETCH_INTERVAL)
                continue
            
            logger.info(f"Fetching quotes for {len(symbols_to_fetch)} symbols: {symbols_to_fetch}")
            
            # Fetch quotes for each symbol
            for symbol in symbols_to_fetch:
                try:
                    quote_data = get_real_time_quote(symbol)
                    logger.info(f"Fetched quote for {symbol}: {quote_data}")
                    
                    if quote_data and not quote_data.get("error"):
                        logger.info(f"Broadcasting {symbol} to subscribers")
                        # Broadcast to subscribed clients
                        await manager.broadcast_to_subscribers(symbol, quote_data)
                        logger.info(f"Broadcast complete for {symbol}")
                    else:
                        logger.warning(f"Error or no data for {symbol}: {quote_data.get('error', 'Unknown error')}")
                
                except Exception as e:
                    logger.error(f"Error fetching quote for {symbol}: {e}")
                    # Send error message to subscribed clients
                    error_data = {
                        "price": 0,
                        "change": 0,
                        "change_percent": 0,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    await manager.broadcast_to_subscribers(symbol, error_data)
            
            # Wait before next fetch
            await asyncio.sleep(FETCH_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in quote fetcher task: {e}")
            # Continue on error
            await asyncio.sleep(FETCH_INTERVAL)


async def start_quote_fetcher() -> None:
    """
    Start the background quote fetcher task.
    Called from FastAPI startup event.
    """
    global quote_fetcher_task
    
    if quote_fetcher_task is None:
        logger.info(f"Starting quote fetcher background task (interval: {FETCH_INTERVAL}s)")
        quote_fetcher_task = asyncio.create_task(fetch_and_broadcast_quotes())
    else:
        logger.warning("Quote fetcher task is already running")


async def stop_quote_fetcher() -> None:
    """
    Stop the background quote fetcher task.
    Called from FastAPI shutdown event.
    """
    global quote_fetcher_task
    
    if quote_fetcher_task is not None:
        logger.info("Stopping quote fetcher background task")
        quote_fetcher_task.cancel()
        try:
            await quote_fetcher_task
        except asyncio.CancelledError:
            logger.info("Quote fetcher task stopped")
        quote_fetcher_task = None


def stop_quote_fetcher(app) -> None:
    """Stop the background quote fetcher task on app shutdown."""
    async def shutdown():
        global quote_fetcher_task
        if quote_fetcher_task:
            logger.info("Stopping quote fetcher background task")
            quote_fetcher_task.cancel()
            try:
                await quote_fetcher_task
            except asyncio.CancelledError:
                pass
    
    app.add_event_handler("shutdown", shutdown)
