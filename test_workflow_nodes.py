"""Debug which node is hanging."""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test():
    from src.workflow.state import WorkflowState
    from src.workflow.langgraph_nodes import router_node, rag_node
    
    try:
        # Test router node
        logger.info("Testing router_node...")
        initial_state: WorkflowState = {
            "message": "What is Apple stock price?",
            "agent": "",
            "reason": "",
        }
        
        router_result = await asyncio.wait_for(
            router_node(initial_state),
            timeout=5
        )
        logger.info(f"Router result: {router_result}")
        
        # Test rag node
        logger.info("Testing rag_node...")
        rag_result = await asyncio.wait_for(
            rag_node(router_result),
            timeout=5
        )
        logger.info(f"RAG result: {rag_result['agent']}, context length: {len(rag_result.get('context', []))}")
        
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout: {e}")
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
