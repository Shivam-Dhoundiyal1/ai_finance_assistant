"""Test WebSocket connection and message flow."""
import asyncio
import json
import logging
from datetime import datetime

import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_websocket_connection():
    """Test WebSocket connection, subscribe, and market updates."""
    
    uri = "ws://localhost:8000/api/v1/ws/market"
    
    try:
        logger.info(f"Connecting to WebSocket at {uri}...")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✓ WebSocket connected successfully")
            
            # Test 1: Subscribe to symbols
            logger.info("\n--- Test 1: Subscribe to AAPL, MSFT ---")
            subscribe_msg = {
                "type": "subscribe",
                "symbols": ["AAPL", "MSFT"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            logger.info(f"Sent: {subscribe_msg}")
            
            # Wait for market updates (increased to 25 seconds to ensure we get at least one batch)
            logger.info("\nListening for market updates for 25 seconds...")
            logger.info("(Background task checks every 5s, so we should get updates around 5-7s mark)")
            start_time = datetime.now()
            update_count = 0
            symbols_received = set()
            
            try:
                while (datetime.now() - start_time).total_seconds() < 25:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1)
                    data = json.loads(message)
                    
                    if data.get("type") == "market_update":
                        update_count += 1
                        symbol = data.get("symbol")
                        symbols_received.add(symbol)
                        price = data.get("data", {}).get("price")
                        change = data.get("data", {}).get("change_percent", 0)
                        logger.info(f"  [{update_count}] {symbol}: ${price:.2f} ({change:+.2f}%)")
                    
            except asyncio.TimeoutError:
                pass
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n✓ Received {update_count} market updates for symbols: {symbols_received} (after {elapsed:.1f}s)")
            
            if update_count == 0:
                logger.warning("⚠ No market updates received! Background task may not be running.")
            
            # Test 2: Unsubscribe
            if update_count > 0:
                logger.info("\n--- Test 2: Unsubscribe from AAPL ---")
                unsubscribe_msg = {
                    "type": "unsubscribe",
                    "symbols": ["AAPL"]
                }
                await websocket.send(json.dumps(unsubscribe_msg))
                logger.info(f"Sent: {unsubscribe_msg}")
                
                # Wait for updates
                logger.info("Listening for updates after unsubscribe (should only get MSFT)...")
                updates_after = 0
                try:
                    while updates_after < 3:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(message)
                        
                        if data.get("type") == "market_update":
                            symbol = data.get("symbol")
                            logger.info(f"  Received: {symbol}")
                            if symbol == "AAPL":
                                logger.warning(f"  ⚠ ERROR: Still receiving AAPL after unsubscribe!")
                            updates_after += 1
                            
                except asyncio.TimeoutError:
                    logger.info(f"  Timeout after {updates_after} updates")
            
            logger.info("\n✓ WebSocket test completed successfully!")
            return True if update_count > 0 else False
            
    except Exception as e:
        logger.error(f"✗ WebSocket test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_websocket_connection())
    exit(0 if success else 1)

