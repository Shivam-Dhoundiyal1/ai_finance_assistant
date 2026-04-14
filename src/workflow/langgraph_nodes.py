"""LangGraph nodes for the Finnie workflow."""
from typing import Any

from src.core.config import get_settings
from src.rag.retriever import retrieve_context
from src.workflow.state import WorkflowState


def _get_llm():
    """Return configured LLM (OpenAI or fallback)."""
    s = get_settings()
    if s.llm_provider == "openai" and s.openai_api_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=s.llm_model,
            temperature=s.llm_temperature,
            max_tokens=s.llm_max_tokens,
            api_key=s.openai_api_key,
        )
    if s.llm_provider == "gemini" and s.gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=s.llm_model or "gemini-pro",
            temperature=s.llm_temperature,
            max_tokens=s.llm_max_tokens,
            google_api_key=s.gemini_api_key,
        )
    # Fallback: no API key
    return None


def _agent_system_prompt(agent: str, reason: str) -> str:
    base = (
        "You are a friendly financial education assistant. "
        "You explain concepts clearly and avoid giving specific investment advice. "
        "Always add a brief disclaimer when discussing money (e.g., 'This is for education only; consider consulting a financial advisor'). "
    )
    role = {
        "finance_qa": "You answer general financial education questions using the provided context when relevant.",
        "portfolio": "You help users understand portfolio allocation, diversification, and rebalancing. Use any portfolio data provided.",
        "market": "You explain market data and stock quotes. Use the provided market data when available.",
        "goal_planning": "You help with financial goals, retirement planning, and risk tolerance. Be encouraging and practical.",
        "news": "You summarize and contextualize financial news. Stay factual and cite when possible.",
        "tax": "You explain tax concepts, IRAs, 401(k)s, Roth accounts, and capital gains in simple terms.",
    }.get(agent, "You answer financial questions in a helpful, educational way.")
    return base + " " + role + f" (Routing reason: {reason})"


def _format_context(context: list[dict[str, Any]]) -> str:
    if not context:
        return "(No retrieved documents)"
    parts = []
    for i, c in enumerate(context, 1):
        text = (c.get("text") or "").strip()
        src = c.get("source") or "Unknown"
        if text:
            parts.append(f"[{i}] {text}\nSource: {src}")
    return "\n\n".join(parts) if parts else "(No retrieved documents)"


def _format_sources(context: list[dict[str, Any]]) -> list[str]:
    seen = set()
    out = []
    for c in context:
        src = c.get("source")
        if src and src not in seen:
            seen.add(src)
            out.append(src)
    return out


async def router_node(state: WorkflowState) -> WorkflowState:
    """Intelligent routing using LLM-based orchestrator."""
    try:
        from src.workflow.intelligent_router import intelligent_route_query
        agent, reason, confidence = await intelligent_route_query(state["message"])
        
        return {
            **state,
            "agent": agent,
            "reason": reason,
            "routing_confidence": confidence,
        }
    except Exception:
        # Generic fallback
        return {
            **state,
            "agent": "finance_qa",
            "reason": "General financial education",
            "routing_confidence": 0.0,
        }


async def rag_node(state: WorkflowState) -> WorkflowState:
    """Retrieve relevant context from the knowledge base."""
    s = get_settings()
    top_k = s.rag_top_k
    
    try:
        context = retrieve_context(state["message"], top_k=top_k)
    except Exception:
        context = []
    
    return {
        **state,
        "context": context,
    }


async def data_enrichment_node(state: WorkflowState) -> WorkflowState:
    """Enrich with market/portfolio data for specific agents."""
    market_data = None
    portfolio_data = None
    
    # Get market data for market agent
    if state["agent"] == "market":
        try:
            from src.data.market_service import get_quote_for_message
            market_data = get_quote_for_message(state["message"])
        except Exception:
            pass
    
    # Get portfolio data for portfolio agent
    if state["agent"] == "portfolio":
        try:
            from src.data.portfolio_service import get_user_portfolio
            portfolio_data = get_user_portfolio("default")
        except Exception:
            pass
    
    return {
        **state,
        "market_data": market_data,
        "portfolio_data": portfolio_data,
    }


async def llm_node(state: WorkflowState) -> WorkflowState:
    """Generate response using selected agent's LLM."""
    try:
        # Get agent by name
        agent_name = state["agent"]
        
        if agent_name == "finance_qa":
            from src.agents.finance_qa import FinanceQAAgent
            agent = FinanceQAAgent()
        elif agent_name == "market":
            from src.agents.market import MarketAgent
            agent = MarketAgent()
        elif agent_name == "portfolio":
            from src.agents.portfolio import PortfolioAnalysisAgent
            agent = PortfolioAnalysisAgent()
        elif agent_name == "goal_planning":
            from src.agents.goal_planning import GoalPlanningAgent
            agent = GoalPlanningAgent()
        elif agent_name == "news":
            from src.agents.news import NewsSynthesizerAgent
            agent = NewsSynthesizerAgent()
        elif agent_name == "tax":
            from src.agents.tax import TaxEducationAgent
            agent = TaxEducationAgent()
        else:
            # Fallback to finance_qa
            from src.agents.finance_qa import FinanceQAAgent
            agent = FinanceQAAgent()
        
        # Prepare additional data for agent
        additional_data = {}
        if state["agent"] == "market" and state.get("market_data"):
            additional_data["market_data"] = state["market_data"]
        elif state["agent"] == "portfolio" and state.get("portfolio_data"):
            additional_data["portfolio_data"] = state["portfolio_data"]
        
        # Generate response using agent's LLM
        response = await agent.generate_response(
            message=state["message"],
            context=state.get("context"),
            additional_data=additional_data if additional_data else None
        )
        
        return {
            **state,
            "response": response,
            "success": True
        }
        
    except Exception as e:
        # Enhanced error handling with classified fallbacks
        error_responses = {
            "api_error": "I'm having trouble accessing market data right now. Using cached information.",
            "llm_error": "I encountered an error processing your request. Please try rephrasing your question.",
            "agent_error": "The specialized agent is temporarily unavailable. Please try again in a moment.",
            "general_error": "I'm experiencing technical difficulties. Please try again later."
        }
        
        error_type = _classify_error(e)
        fallback_response = error_responses.get(error_type, error_responses["general_error"])
        
        return {
            **state,
            "response": fallback_response,
            "success": False,
            "error": str(e)
        }


def _classify_error(error: Exception) -> str:
    """Classify error type for appropriate fallback."""
    error_str = str(error).lower()
    
    if "api" in error_str or "network" in error_str:
        return "api_error"
    elif "llm" in error_str or "model" in error_str:
        return "llm_error"
    elif "agent" in error_str:
        return "agent_error"
    else:
        return "general_error"


async def response_formatter_node(state: WorkflowState) -> WorkflowState:
    """Format final response with sources and metadata."""
    try:
        # Extract sources from context if available
        sources = []
        if state.get("context"):
            for ctx in state["context"]:
                if isinstance(ctx, dict) and "source" in ctx:
                    sources.append(ctx["source"])
        
        return {
            **state,
            "sources": list(set(sources)),  # Remove duplicates
        }
    except Exception:
        return state


def _format_sources(context: list[dict[str, Any]] | None) -> list[str]:
    """Extract and format sources from context."""
    if not context:
        return []
    
    sources = []
    for ctx in context:
        if isinstance(ctx, dict) and "source" in ctx:
            sources.append(ctx["source"])
    
    return list(set(sources))  # Remove duplicates
