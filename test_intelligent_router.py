"""Test the intelligent router implementation."""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

async def test_router():
    try:
        from src.workflow.intelligent_router import intelligent_route_query
        
        # Test different types of queries
        test_cases = [
            "What is diversification?",
            "AAPL stock price",
            "How should I allocate my portfolio?",
            "What are the latest financial news?",
            "How do 401k work?",
            "What's my risk tolerance?",
        ]
        
        print("🧠 Testing Intelligent Router:")
        print("=" * 50)
        
        for query in test_cases:
            try:
                agent, reason, confidence = await intelligent_route_query(query)
                print(f"Query: {query}")
                print(f"Agent: {agent} | Confidence: {confidence:.2f}")
                print(f"Reason: {reason}")
                print("-" * 30)
            except Exception as e:
                print(f"❌ Error for '{query}': {e}")
                print("-" * 30)
        
        print("✅ Router testing complete!")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        print("Make sure OPENAI_API_KEY or GEMINI_API_KEY is set in .env")

if __name__ == "__main__":
    asyncio.run(test_router())
