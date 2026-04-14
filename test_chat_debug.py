"""Test the chat endpoint directly."""
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_chat():
    """Test chat endpoint."""
    try:
        from src.api.main import app
        from src.api.main import chat
        from src.api.main import ChatRequest
        
        logger.info("Testing chat endpoint...")
        
        request = ChatRequest(message="What is a stock?")
        logger.info(f"Request: {request}")
        
        response = await chat(request)
        logger.info(f"Response: {response}")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


async def test_workflow():
    """Test the workflow directly."""
    try:
        from src.workflow.langgraph_workflow import run_langgraph_workflow
        
        logger.info("Testing workflow...")
        result = await run_langgraph_workflow("What is a stock?")
        logger.info(f"Workflow result: {result}")
        
    except Exception as e:
        logger.error(f"Workflow error: {e}", exc_info=True)


async def test_router():
    """Test the intelligent router."""
    try:
        from src.workflow.intelligent_router import intelligent_route_query
        
        logger.info("Testing router...")
        agent, reason, confidence = await intelligent_route_query("What is a stock?")
        logger.info(f"Router result: agent={agent}, reason={reason}, confidence={confidence}")
        
    except Exception as e:
        logger.error(f"Router error: {e}", exc_info=True)


async def test_llm():
    """Test LLM availability."""
    try:
        from src.agents.finance_qa import FinanceQAAgent
        
        logger.info("Testing LLM...")
        agent = FinanceQAAgent()
        logger.info(f"Agent LLM: {agent.llm}")
        
        if agent.llm:
            # Try to generate a response
            response = await agent.generate_response("What is a stock?")
            logger.info(f"Agent response: {response}")
        else:
            logger.warning("No LLM configured!")
            
    except Exception as e:
        logger.error(f"LLM error: {e}", exc_info=True)


async def main():
    """Run all tests."""
    print("\n=== Testing Router ===")
    await test_router()
    
    print("\n=== Testing LLM ===")
    await test_llm()
    
    print("\n=== Testing Workflow ===")
    await test_workflow()


if __name__ == "__main__":
    asyncio.run(main())
