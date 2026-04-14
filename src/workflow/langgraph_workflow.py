"""LangGraph workflow implementation for Finnie."""
from typing import Any

from langgraph.graph import StateGraph, END

from src.workflow.langgraph_nodes import (
    router_node,
    rag_node,
    data_enrichment_node,
    llm_node,
    response_formatter_node,
)
from src.workflow.state import WorkflowState


def create_workflow() -> StateGraph:
    """Create and configure the LangGraph workflow."""
    
    # Initialize the workflow with our state
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("data_enrichment", data_enrichment_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("response_formatter", response_formatter_node)
    
    # Define the flow
    workflow.set_entry_point("router")
    
    # Linear flow: router -> rag -> data_enrichment -> llm -> response_formatter
    workflow.add_edge("router", "rag")
    workflow.add_edge("rag", "data_enrichment")
    workflow.add_edge("data_enrichment", "llm")
    workflow.add_edge("llm", "response_formatter")
    workflow.add_edge("response_formatter", END)
    
    return workflow


# Compile the workflow
app = create_workflow().compile()


async def run_langgraph_workflow(message: str) -> dict[str, Any]:
    """
    Execute the LangGraph workflow.
    
    Args:
        message: The user's input message
        
    Returns:
        Dict with response, agent, reason, sources, and routing_confidence
    """
    # Initialize state with the user's message
    initial_state: WorkflowState = {
        "message": message,
        "agent": "",
        "reason": "",
    }
    
    # Execute the workflow
    final_state = await app.ainvoke(initial_state)
    
    # Extract and return the relevant fields
    return {
        "response": final_state.get("response", ""),
        "agent": final_state.get("agent", ""),
        "reason": final_state.get("reason", ""),
        "sources": final_state.get("sources", []),
        "routing_confidence": final_state.get("routing_confidence", 0.0),
    }


# Optional: Add visualization support
def get_workflow_graph():
    """Get the workflow graph for visualization."""
    return create_workflow()
