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


def _after_llm(state: WorkflowState) -> str:
    """Route after LLM based on execution mode."""
    execution_mode = state.get("execution_mode", "fast")
    
    if execution_mode == "deep":
        return "critic"  # Run critic for complex queries
    else:
        return "response_formatter"  # Skip critic for simple queries


def _after_critic(state: WorkflowState) -> str:
    """Smart retry logic with confidence thresholds."""
    execution_mode = state.get("execution_mode", "fast")
    agent = state.get("agent", "")
    
    # Always skip critic for fast mode agents
    if execution_mode == "fast":
        return "response_formatter"
    
    # Check critic status and confidence
    critic_status = state.get("critic_status", "pass")
    critic_confidence = state.get("critic_confidence", 0.0)
    
    # Pass if critic says so or confidence is low (uncertain critic)
    if critic_status == "pass" or critic_confidence < 0.6:
        return "response_formatter"
    
    # Retry only if we have attempts left and critic is confident
    if state.get("attempt_count", 0) < state.get("max_attempts", 2):
        return "llm"
    
    # Max attempts reached, format response
    return "response_formatter"


def _route_after_router(state: WorkflowState) -> str:
    """Route to appropriate next node based on agent type."""
    agent = state.get("agent", "llm")
    
    if agent == "llm":
        return "llm"  # Direct to LLM, skip RAG/Data
    elif agent == "data_enrichment":
        return "data_enrichment"  # Skip RAG, get data
    elif agent in ["rag", "portfolio"]:
        return "rag"  # Full path: RAG -> Data -> LLM
    else:
        return "llm"  # Safe default


def _route_after_rag(state: WorkflowState) -> str:
    """Route after RAG based on agent type."""
    agent = state.get("agent", "llm")
    
    if agent in ["rag", "portfolio"]:
        return "data_enrichment"  # Continue to data enrichment
    else:
        return "llm"  # Skip to LLM


def _route_after_data_enrichment(state: WorkflowState) -> str:
    """Route after data enrichment - always go to LLM."""
    return "llm"


def create_workflow() -> StateGraph:
    """Create and configure the optimized LangGraph workflow."""
    
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
    
    # Agent-aware conditional routing
    workflow.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "llm": "llm",
            "data_enrichment": "data_enrichment",
            "rag": "rag",
        },
    )
    
    # Route after RAG
    workflow.add_conditional_edges(
        "rag",
        _route_after_rag,
        {
            "data_enrichment": "data_enrichment",
            "llm": "llm",
        },
    )
    
    # Route after data enrichment
    workflow.add_edge("data_enrichment", "llm")
    
    # Conditional routing after LLM based on execution mode
    workflow.add_conditional_edges(
        "llm",
        _after_llm,
        {
            "critic": "critic",
            "response_formatter": "response_formatter",
        },
    )
    
    # Conditional routing after critic
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
        "execution_mode": "fast",  # Default to fast mode
        "attempt_count": 0,
        "max_attempts": 2,
        "execution_trace": [],
        "critic_status": "",
        "critic_reason": "",
        "critic_confidence": 0.0,
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
