"""Simple test to verify LangGraph implementation works."""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

async def test_langgraph():
    try:
        from src.workflow.langgraph_workflow import run_langgraph_workflow
        print("✅ LangGraph import successful!")
        
        # Test with a simple message
        result = await run_langgraph_workflow("What is diversification?")
        print("✅ LangGraph execution successful!")
        print(f"Agent: {result.get('agent')}")
        print(f"Response: {result.get('response', '')[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_langgraph())
    if success:
        print("\n🎉 LangGraph implementation is working!")
    else:
        print("\n💥 LangGraph implementation failed!")
