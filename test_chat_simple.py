"""Test the chat endpoint."""
import asyncio
import httpx


async def test_chat():
    """Test chat API endpoint."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/chat",
                json={"message": "What is a stock?"}
            )
            
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {data}")
            
            if response.status_code == 200:
                print(f"\n✓ Chat working!")
                print(f"  Agent: {data.get('agent')}")
                print(f"  Confidence: {data.get('routing_confidence'):.2%}")
                print(f"  Response: {data.get('response')[:100]}...")
            else:
                print(f"\n✗ Chat failed with status {response.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_chat())
