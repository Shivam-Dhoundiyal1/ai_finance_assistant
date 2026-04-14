"""Debug workflow errors."""
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

from src.workflow.langgraph_workflow import run_langgraph_workflow

async def test():
    try:
        print("Testing workflow...")
        result = await asyncio.wait_for(
            run_langgraph_workflow("What is Apple stock price?"),
            timeout=10
        )
        print("Result:", result)
    except asyncio.TimeoutError:
        print("ERROR: Workflow timed out after 10 seconds")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
