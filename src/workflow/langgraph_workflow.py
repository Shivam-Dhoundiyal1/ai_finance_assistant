"""LangGraph workflow implementation for Finnie."""
from typing import Any

from langgraph.graph import StateGraph, END

from src.workflow.langgraph_nodes import (
    router_node,
    rag_node,
    data_enrichment_node,
    llm_node,
    critic_node,
    response_formatter_node,
)
from src.workflow.state import WorkflowState


def _after_critic(state: WorkflowState) -> str:
    if state.get("critic_status") == "pass":
        return "response_formatter"
    if state.get("attempt_count", 0) < state.get("max_attempts", 2):
        return "llm"
    return "response_formatter"


def create_workflow() -> StateGraph:
    """Create and configure the LangGraph workflow."""
    
    # Initialize the workflow with our state
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("data_enrichment", data_enrichment_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("response_formatter", response_formatter_node)
    
    # Define the flow
    workflow.set_entry_point("router")
    
    # Linear flow: router -> rag -> data_enrichment -> llm -> response_formatter
    workflow.add_edge("router", "rag")
    workflow.add_edge("rag", "data_enrichment")
    workflow.add_edge("data_enrichment", "llm")
    workflow.add_edge("llm", "critic")
    workflow.add_conditional_edges(
        "critic",
        _after_critic,
        {
            "llm": "llm",
            "response_formatter": "response_formatter",
        },
    )
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
        "attempt_count": 0,
        "max_attempts": 2,
        "execution_trace": [],
        "critic_status": "",
        "critic_reason": "",
        "retry_reason": "",
        "fallback_agent": "",
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
        "attempt_count": final_state.get("attempt_count", 0),
        "execution_trace": final_state.get("execution_trace", []),
        "critic_status": final_state.get("critic_status", ""),
    }


# Optional: Add visualization support
def get_workflow_graph():
    """Get the workflow graph for visualization."""
    return create_workflow()
