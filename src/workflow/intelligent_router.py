"""Intelligent LLM-based router for query orchestration."""
from typing import Any, Dict, List, Tuple

from src.core.config import get_settings


def _is_greeting(message: str) -> bool:
    """True for short greeting messages that should stay in general chat."""
    text = (message or "").strip().lower()
    if not text:
        return False
    greetings = [
        "hi",
        "hello",
        "hey",
        "hi there",
        "hello there",
        "good morning",
        "good afternoon",
        "good evening",
    ]
    return text in greetings or text.startswith(tuple(g for g in greetings if " " not in g))


def _is_obvious_quote_request(message: str) -> bool:
    """Return True when a message is clearly asking for a stock quote with no need for LLM routing."""
    text = (message or "").lower()
    quote_terms = [
        "quote",
        "stock price",
        "share price",
        "ticker",
        "symbol",
        "market price",
        "current price",
        "trading at",
        "latest price",
        "stock quote",
    ]
    symbols = [
        "aapl", "apple",
        "msft", "microsoft",
        "tsla", "tesla",
        "nvda", "nvidia",
        "googl", "google",
        "amzn", "amazon",
        "meta",
        "nflx", "netflix",
        "amd",
        "intel",
    ]
    if any(term in text for term in quote_terms):
        return True
    return any(symbol in text for symbol in symbols)


def _keyword_route(message: str) -> Tuple[str, str, float]:
    """Deterministic fallback routing for test and no-LLM environments."""
    text = message.lower()

    if _is_obvious_quote_request(text):
        return "market", "Keyword-based market routing", 0.6
    if any(keyword in text for keyword in ["portfolio", "allocation", "rebalance", "holdings"]):
        return "portfolio", "Keyword-based portfolio routing", 0.6
    if any(keyword in text for keyword in ["ira", "401k", "roth", "tax", "capital gains", "deduction"]):
        return "tax", "Keyword-based tax routing", 0.6
    if any(keyword in text for keyword in ["retirement", "goal", "save for", "risk tolerance", "plan for"]):
        return "goal_planning", "Keyword-based goal planning routing", 0.6
    if any(keyword in text for keyword in ["news", "headline", "current events", "latest"]):
        return "news", "Keyword-based news routing", 0.6
    return "finance_qa", "General financial education", 0.0


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
        return _keyword_route(message)
        
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
                    if confidence < 0.5:
                        return (
                            "finance_qa",
                            f"Low routing confidence fallback from {agent}: {reason}",
                            confidence,
                        )
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
    if _is_greeting(message):
        return "llm", "Greeting detected; route to friendly general chat", 1.0
    if _is_obvious_quote_request(message):
        return "market", "Direct market route: clear stock quote request detected", 0.9

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

    keyword_agent, keyword_reason, keyword_confidence = _keyword_route(message)
    if keyword_agent != "finance_qa":
        return keyword_agent, keyword_reason, keyword_confidence

    llm = _get_llm()
    if not llm:
        return keyword_agent, keyword_reason, keyword_confidence

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
                    if confidence < 0.5:
                        return (
                            "finance_qa",
                            f"Low routing confidence fallback from {agent}: {reason}",
                            confidence,
                        )
                    return agent, reason, confidence
        
        # Fallback if parsing fails - ask LLM to rephrase
        return await rephrase_and_retry(message)
        
    except Exception:
        # Generic error - return default agent
        return "finance_qa", "General financial education", 0.0


