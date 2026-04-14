"""Simple WebSocket diagnostic test."""
import asyncio
import json
import logging

import websockets

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test():
    uri = "ws://localhost:8000/api/v1/ws/market"
    
    try:
        async with websockets.connect(uri) as ws:
            logger.info("Connected to WebSocket")
            
            # Send subscribe
            msg = {"type": "subscribe", "symbols": ["AAPL"]}
            await ws.send(json.dumps(msg))
            logger.info(f"Sent: {msg}")
            
            # Listen for 30 seconds
            start = asyncio.get_event_loop().time()
            count = 0
            
            while asyncio.get_event_loop().time() - start < 30:
                try:
                    logger.info("Waiting for message...")
                    msg = await asyncio.wait_for(ws.recv(), timeout=3)
                    data = json.loads(msg)
                    count += 1
                    logger.info(f"[{count}] Received: {data}")
                except asyncio.TimeoutError:
                    logger.info("No message (timeout)")
                except Exception as e:
                    logger.error(f"Error: {e}")
                    break
                    
            logger.info(f"Done. Received {count} messages")
                    
    except Exception as e:
        logger.error(f"Failed: {e}")


if __name__ == "__main__":
    asyncio.run(test())
