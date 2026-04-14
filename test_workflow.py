"""Test LangGraph workflow directly."""
import asyncio
from src.workflow.langgraph_workflow import run_langgraph_workflow

async def test():
    try:
        print("Testing workflow with: 'What is Apple stock price?'")
        result = await run_langgraph_workflow("What is Apple stock price?")
        print("\n✓ Result:", result)
        return result
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test())
