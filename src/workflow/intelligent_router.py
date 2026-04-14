"""Intelligent LLM-based router for query orchestration."""
from typing import Any, Dict, List, Tuple

from src.core.config import get_settings


def _get_llm():
    """Return configured LLM for routing."""
    s = get_settings()
    if s.llm_provider == "openai" and s.openai_api_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=s.llm_model,
            temperature=0.1,  # Lower temperature for routing
            max_tokens=100,
            api_key=s.openai_api_key,
        )
    if s.llm_provider == "gemini" and s.gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=s.llm_model or "gemini-pro",
            temperature=0.1,
            max_tokens=100,
            google_api_key=s.gemini_api_key,
        )
    return None


async def rephrase_and_retry(message: str) -> Tuple[str, str, float]:
    """Ask LLM to rephrase the message for better routing."""
    llm = _get_llm()
    if not llm:
        return "finance_qa", "General financial education", 0.0
        
    rephrase_prompt = f"""
    The user said: "{message}"
    
    Please rephrase this question in a clearer way that would be easier for a routing system to understand.
    Respond in the same format: AGENT|agent_name|confidence|reasoning
    
    Available agents: finance_qa, portfolio, market, goal_planning, news, tax
    """
    
    try:
        from langchain_core.messages import HumanMessage
        result = await llm.ainvoke(HumanMessage(content=rephrase_prompt))
        response = result.content if hasattr(result, "content") else str(result)
        
        # Parse rephrased response
        if "|" in response:
            parts = response.strip().split("|")
            if len(parts) >= 4 and parts[0] == "AGENT":
                agent = parts[1].strip()
                confidence = float(parts[2].strip())
                reason = parts[3].strip()
                
                # Validate agent name
                valid_agents = ["finance_qa", "portfolio", "market", "goal_planning", "news", "tax"]
                if agent in valid_agents:
                    return agent, reason, confidence
    except Exception:
        pass
    
    # Final fallback
    return "finance_qa", "General financial education", 0.0


async def intelligent_route_query(
    message: str, 
    conversation_history: List[Dict[str, str]] | None = None
) -> Tuple[str, str, float]:
    """
    Use LLM to intelligently route queries to appropriate agents.
    
    Returns:
        tuple: (agent_name, reason, confidence_score)
    """
    routing_prompt = f"""
You are an intelligent financial assistant router. Analyze the user query and route it to the most appropriate agent.

Available agents:
- finance_qa: General financial education, definitions, concepts, explanations
- portfolio: Portfolio analysis, allocation, diversification, rebalancing, holdings
- market: Stock prices, market data, trading, quotes, symbols, market analysis
- goal_planning: Financial goals, retirement planning, savings, risk tolerance, planning
- news: Financial news, current events, market updates, headlines
- tax: Tax questions, IRAs, 401(k)s, Roth accounts, deductions, capital gains

User query: "{message}"

Analyze the query and respond in this exact format:
AGENT|agent_name|confidence|reasoning

Where:
- AGENT is literal
- agent_name is one of: finance_qa, portfolio, market, goal_planning, news, tax
- confidence is a number from 0.0 to 1.0 indicating routing confidence
- reasoning explains why this agent was chosen

Example response: AGENT|market|0.9|User is asking about stock price
"""

    llm = _get_llm()
    if not llm:
        return "finance_qa", "General financial education", 0.0

    try:
        from langchain_core.messages import HumanMessage
        result = await llm.ainvoke(HumanMessage(content=routing_prompt))
        response = result.content if hasattr(result, "content") else str(result)
        
        # Parse the response
        if "|" in response:
            parts = response.strip().split("|")
            if len(parts) >= 4 and parts[0] == "AGENT":
                agent = parts[1].strip()
                confidence = float(parts[2].strip())
                reason = parts[3].strip()
                
                # Validate agent name
                valid_agents = ["finance_qa", "portfolio", "market", "goal_planning", "news", "tax"]
                if agent in valid_agents:
                    return agent, reason, confidence
        
        # Fallback if parsing fails - ask LLM to rephrase
        return await rephrase_and_retry(message)
        
    except Exception:
        # Generic error - return default agent
        return "finance_qa", "General financial education", 0.0


