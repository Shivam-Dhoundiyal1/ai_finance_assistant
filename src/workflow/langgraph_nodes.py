"""LangGraph nodes for the Finnie workflow."""
import re
from typing import Any

from src.agents import finance_qa, goal_planning, market, news, portfolio, tax
from src.core.config import get_settings
from src.rag import retriever
from src.workflow import intelligent_router
from src.workflow.state import WorkflowState


async def intelligent_route_query(*args, **kwargs):
    return await intelligent_router.intelligent_route_query(*args, **kwargs)


def retrieve_context(*args, **kwargs):
    return retriever.retrieve_context(*args, **kwargs)


def FinanceQAAgent(*args, **kwargs):
    return finance_qa.FinanceQAAgent(*args, **kwargs)


def GoalPlanningAgent(*args, **kwargs):
    return goal_planning.GoalPlanningAgent(*args, **kwargs)


def MarketAgent(*args, **kwargs):
    return market.MarketAgent(*args, **kwargs)


def NewsSynthesizerAgent(*args, **kwargs):
    return news.NewsSynthesizerAgent(*args, **kwargs)


def PortfolioAnalysisAgent(*args, **kwargs):
    return portfolio.PortfolioAnalysisAgent(*args, **kwargs)


def TaxEducationAgent(*args, **kwargs):
    return tax.TaxEducationAgent(*args, **kwargs)


def _append_trace(
    state: WorkflowState,
    node_name: str,
    status: str,
    agent: str | None = None,
) -> list[dict[str, Any]]:
    trace = list(state.get("execution_trace", []))
    trace.append(
        {
            "node": node_name,
            "status": status,
            "agent": agent or state.get("agent", ""),
            "attempt_count": state.get("attempt_count", 0),
        }
    )
    return trace


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


def _is_goal_planning_query(message: str) -> bool:
    msg = (message or "").lower()
    goal_terms = [
        "goal",
        "target",
        "reach",
        "accumulate",
        "save",
        "invest",
        "crore",
        "lakh",
        "retire",
    ]
    return any(t in msg for t in goal_terms)


def _extract_numeric_tokens(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?", text or "")


def _has_target_and_timeline(message: str) -> bool:
    msg = (message or "").lower()
    has_amount_hint = bool(_extract_numeric_tokens(msg)) and any(
        t in msg
        for t in ["crore", "lakh", "rs", "rupee", "inr", "$", "million", "target", "amount"]
    )
    has_time_hint = bool(
        re.search(r"\b\d+(?:\.\d+)?\s*(year|years|yr|yrs|month|months)\b", msg)
    )
    return has_amount_hint and has_time_hint


def _requires_numeric_planning(message: str, response: str) -> bool:
    if not _has_target_and_timeline(message):
        return False
    rsp = (response or "").lower()
    has_number = bool(_extract_numeric_tokens(rsp))
    has_required_metric = any(
        p in rsp
        for p in [
            "required investment",
            "required monthly",
            "monthly investment",
            "per month",
            "yearly savings",
            "annual savings",
            "per year",
        ]
    )
    return not (has_number and has_required_metric)


def _missing_personalization(message: str, response: str) -> bool:
    msg_numbers = _extract_numeric_tokens(message)
    if not msg_numbers:
        return False
    rsp_numbers = set(_extract_numeric_tokens(response))
    return not any(n in rsp_numbers for n in msg_numbers)


def _is_generic_response(response: str) -> bool:
    rsp = (response or "").lower()
    generic_phrases = [
        "save more",
        "invest wisely",
        "it depends",
        "consider your goals",
        "consult a financial advisor",
        "diversify your portfolio",
        "be disciplined",
        "do your own research",
    ]
    return any(p in rsp for p in generic_phrases)


def _is_context_query(message: str) -> bool:
    msg = (message or "").lower()
    context_terms = [
        "war",
        "crisis",
        "recession",
        "conflict",
        "geopolitical",
        "ai",
        "artificial intelligence",
        "technology shift",
        "future",
        "automation",
    ]
    return any(t in msg for t in context_terms)


def _missing_context_structure(message: str, response: str) -> bool:
    if not _is_context_query(message):
        return False
    rsp = (response or "").lower()
    has_risk = "risk strategy" in rsp or "risk" in rsp
    has_opportunity = "opportunity strategy" in rsp or "opportunity" in rsp
    has_action = "actionable advice" in rsp or "action" in rsp or "next step" in rsp
    return not (has_risk and has_opportunity and has_action)


def _is_ambiguous_query(message: str) -> bool:
    msg = (message or "").strip().lower()
    if len(msg) < 8:
        return True
    vague_terms = ["help me", "what should i do", "advice", "suggest", "plan"]
    has_vague = any(t in msg for t in vague_terms)
    lacks_detail = len(_extract_numeric_tokens(msg)) == 0 and not _is_context_query(msg)
    return has_vague and lacks_detail


def _is_relevant_response(message: str, response: str) -> bool:
    msg_tokens = set(re.findall(r"[a-z]{4,}", (message or "").lower()))
    rsp_tokens = set(re.findall(r"[a-z]{4,}", (response or "").lower()))
    if not msg_tokens:
        return True
    overlap = msg_tokens.intersection(rsp_tokens)
    return len(overlap) >= 2


def _is_greeting_message(message: str) -> bool:
    normalized = re.sub(r"[^a-z\s]", "", (message or "").strip().lower())
    normalized = re.sub(r"\s+", " ", normalized)
    greetings = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening",
        "good afternoon",
        "hello there",
    }
    return normalized in greetings


def _build_low_confidence_estimate(message: str) -> str | None:
    if not _has_target_and_timeline(message):
        return None

    msg = (message or "").lower()
    nums = _extract_numeric_tokens(msg)
    if not nums:
        return None

    years_match = re.search(r"(\d+(?:\.\d+)?)\s*(year|years|yr|yrs)", msg)
    months_match = re.search(r"(\d+(?:\.\d+)?)\s*(month|months)", msg)
    if years_match:
        months = float(years_match.group(1)) * 12
    elif months_match:
        months = float(months_match.group(1))
    else:
        return None

    raw_amount = float(nums[0])
    if "crore" in msg:
        target = raw_amount * 10_000_000
    elif "lakh" in msg:
        target = raw_amount * 100_000
    elif "million" in msg:
        target = raw_amount * 1_000_000
    else:
        target = raw_amount

    if months <= 0:
        return None

    annual_return = 0.10
    monthly_rate = annual_return / 12
    if monthly_rate > 0:
        monthly = target * monthly_rate / ((1 + monthly_rate) ** months - 1)
    else:
        monthly = target / months

    yearly = monthly * 12
    return (
        "Required Investment:\n"
        f"- Monthly investment: Rs {monthly:,.0f}\n"
        f"- Yearly savings: Rs {yearly:,.0f}\n\n"
        "Assumptions:\n"
        "- 10% expected annual return\n"
        "- Consistent monthly investing over the full period\n\n"
        "Action Plan:\n"
        "- Start SIP immediately and automate monthly contribution\n"
        "- Increase contribution after salary hikes\n"
        "- Review plan quarterly and rebalance if needed"
    )

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
    if _is_greeting_message(state.get("message", "")):
        return {
            **state,
            "agent": "finance_qa",
            "reason": "Greeting detected",
            "routing_confidence": 1.0,
            "is_greeting": True,
            "execution_trace": _append_trace(
                state,
                "router",
                "success",
                "finance_qa",
            ),
        }

    try:
        agent, reason, confidence = await intelligent_route_query(state["message"])
        fallback_agent = "finance_qa" if agent == "finance_qa" and confidence < 0.5 else ""

        return {
            **state,
            "agent": agent,
            "reason": reason,
            "routing_confidence": confidence,
            "fallback_agent": fallback_agent,
            "is_greeting": False,
            "execution_trace": _append_trace(
                state,
                "router",
                "success",
                agent,
            ),
        }
    except Exception as exc:
        # Generic fallback
        return {
            **state,
            "agent": "finance_qa",
            "reason": "General financial education",
            "routing_confidence": 0.0,
            "fallback_agent": "finance_qa",
            "is_greeting": False,
            "error": str(exc),
            "execution_trace": _append_trace(
                state,
                "router",
                "failure",
                "finance_qa",
            ),
        }


async def rag_node(state: WorkflowState) -> WorkflowState:
    """Retrieve relevant context from the knowledge base."""
    if state.get("is_greeting"):
        # Skip retrieval for greetings and keep trace focused on Router -> LLM -> Critic -> Response.
        return {
            **state,
            "context": [],
        }

    s = get_settings()
    top_k = s.rag_top_k
    
    try:
        context = retrieve_context(state["message"], top_k=top_k)
        trace = _append_trace(state, "rag", "success")
    except Exception:
        context = []
        trace = _append_trace(state, "rag", "failure")
    
    return {
        **state,
        "context": context,
        "execution_trace": trace,
    }


async def data_enrichment_node(state: WorkflowState) -> WorkflowState:
    """Enrich with market/portfolio data for specific agents."""
    if state.get("is_greeting"):
        return {
            **state,
            "market_data": None,
            "portfolio_data": None,
        }

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
        "execution_trace": _append_trace(state, "data_enrichment", "success"),
    }


async def llm_node(state: WorkflowState) -> WorkflowState:
    """Generate response using selected agent's LLM."""
    attempt_count = state.get("attempt_count", 0) + 1

    if state.get("is_greeting"):
        return {
            **state,
            "attempt_count": attempt_count,
            "response": "Hi! How can I help you with your finances today?",
            "success": True,
            "execution_trace": _append_trace(
                {**state, "attempt_count": attempt_count},
                "llm",
                "success",
                state.get("agent", "finance_qa"),
            ),
        }

    # Low-confidence fallback: avoid generic response.
    if state.get("routing_confidence", 0.0) < 0.5:
        estimate = _build_low_confidence_estimate(state.get("message", ""))
        if estimate:
            return {
                **state,
                "attempt_count": attempt_count,
                "response": estimate,
                "success": True,
                "execution_trace": _append_trace(
                    {**state, "attempt_count": attempt_count},
                    "llm",
                    "success",
                    state.get("agent", "finance_qa"),
                ),
            }
        if _is_ambiguous_query(state.get("message", "")):
            return {
                **state,
                "attempt_count": attempt_count,
                "response": (
                    "Could you share your target amount, timeline, and monthly investable surplus "
                    "so I can give you a personalized plan?"
                ),
                "success": True,
                "execution_trace": _append_trace(
                    {**state, "attempt_count": attempt_count},
                    "llm",
                    "success",
                    state.get("agent", "finance_qa"),
                ),
            }

    try:
        # Get agent by name
        agent_name = state["agent"]

        if agent_name == "finance_qa":
            agent = FinanceQAAgent()
        elif agent_name == "market":
            agent = MarketAgent()
        elif agent_name == "portfolio":
            agent = PortfolioAnalysisAgent()
        elif agent_name == "goal_planning":
            agent = GoalPlanningAgent()
        elif agent_name == "news":
            agent = NewsSynthesizerAgent()
        elif agent_name == "tax":
            agent = TaxEducationAgent()
        else:
            # Fallback to finance_qa
            agent = FinanceQAAgent()

        # Prepare additional data for agent
        additional_data = {}
        if state["agent"] == "market" and state.get("market_data"):
            additional_data["market_data"] = state["market_data"]
        elif state["agent"] == "portfolio" and state.get("portfolio_data"):
            additional_data["portfolio_data"] = state["portfolio_data"]

        prompt_message = state["message"]

        if _is_goal_planning_query(state["message"]):
            prompt_message = (
                f"{prompt_message}\n\n"
                "Output structure:\n"
                "1. Required Investment\n"
                "2. Assumptions\n"
                "3. Action Plan\n\n"
                "Instructions:\n"
                "- Always compute monthly or yearly investment when goal + time are provided.\n"
                "- Avoid generic advice.\n"
                "- Personalize calculations using user numbers.\n"
                "- Keep answer concise and actionable."
            )

        if _is_context_query(state["message"]):
            prompt_message = (
                f"{prompt_message}\n\n"
                "Context-aware requirements:\n"
                "1. Risk Strategy\n"
                "2. Opportunity Strategy\n"
                "3. Actionable Advice\n"
                "Tie recommendations to the user's context and current conditions."
            )

        if _is_ambiguous_query(state["message"]):
            prompt_message = (
                f"{prompt_message}\n\n"
                "If details are missing, ask one concise clarifying question first or provide a conditional answer with assumptions."
            )

        if attempt_count > 1:
            retry_reason = state.get("retry_reason", "previous response was too weak")
            prompt_message = (
                f"{state['message']}\n\n"
                "Previous response was insufficient. Be specific, structured, and personalized. "
                f"Directly address this issue: {retry_reason}."
            )

        # Generate response using agent's LLM
        response = await agent.generate_response(
            message=prompt_message,
            context=state.get("context"),
            additional_data=additional_data if additional_data else None
        )
        
        return {
            **state,
            "attempt_count": attempt_count,
            "response": response,
            "success": True,
            "execution_trace": _append_trace(
                {**state, "attempt_count": attempt_count},
                "llm",
                "success",
                agent_name,
            ),
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
            "attempt_count": attempt_count,
            "response": fallback_response,
            "success": False,
            "error": str(e),
            "execution_trace": _append_trace(
                {**state, "attempt_count": attempt_count},
                "llm",
                "failure",
                state.get("agent", ""),
            ),
        }


async def critic_node(state: WorkflowState) -> WorkflowState:
    """Evaluate the generated response and decide whether it is acceptable."""
    response = (state.get("response") or "").strip()
    message = (state.get("message") or "").strip()

    failure_phrases = [
        "i encountered an error",
        "technical difficulties",
        "please try rephrasing",
        "specialized agent is temporarily unavailable",
        "demo mode",
    ]

    status = "pass"
    reason = "response accepted"

    if not response:
        status = "fail"
        reason = "empty response"
    elif state.get("is_greeting") and len(response) > 120:
        status = "fail"
        reason = "Greeting should not trigger long response"
    elif len(response) < 40 and not state.get("is_greeting"):
        status = "fail"
        reason = "response too short"
    elif any(phrase in response.lower() for phrase in failure_phrases):
        status = "fail"
        reason = "response contains fallback or error language"
    elif _is_generic_response(response):
        status = "fail"
        reason = "response is too generic"
    elif not _is_relevant_response(message, response):
        status = "fail"
        reason = "response is irrelevant to the user query"
    elif _requires_numeric_planning(message, response):
        status = "fail"
        reason = "Missing numeric financial planning"
    elif _missing_personalization(message, response):
        status = "fail"
        reason = "missing personalization using user's numbers"
    elif _missing_context_structure(message, response):
        status = "fail"
        reason = "contextual query missing risk/opportunity/actionable structure"
    else:
        llm = _get_llm()
        if llm:
            context_preview = _format_context(state.get("context", []))[:1200]
            critic_prompt = f"""
Review the assistant response for quality.

User question: {state['message']}
Agent: {state.get('agent', '')}
Context: {context_preview}
Response: {response}

Strict checks:
- Fail if irrelevant to query.
- Fail if greeting receives long response.
- Fail if numeric goal lacks calculation.
- Fail if context query ignores risk/opportunity/actionable framing.
- Fail if response is generic.

Reply with exactly one line in this format:
PASS|short reason
or
FAIL|short reason
"""
            try:
                from langchain_core.messages import HumanMessage

                result = await llm.ainvoke(HumanMessage(content=critic_prompt))
                critic_text = result.content if hasattr(result, "content") else str(result)
                parts = critic_text.strip().split("|", 1)
                if len(parts) == 2 and parts[0].strip().upper() in {"PASS", "FAIL"}:
                    status = parts[0].strip().lower()
                    reason = parts[1].strip() or reason
            except Exception:
                pass

    next_state = {
        **state,
        "critic_status": status,
        "critic_reason": reason,
        "execution_trace": _append_trace(state, "critic", "success", state.get("agent", "")),
    }
    if status == "fail":
        next_state["retry_reason"] = reason
    return next_state


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
            "execution_trace": _append_trace(state, "response_formatter", "success"),
        }
    except Exception:
        return {
            **state,
            "execution_trace": _append_trace(state, "response_formatter", "failure"),
        }


def _format_sources(context: list[dict[str, Any]] | None) -> list[str]:
    """Extract and format sources from context."""
    if not context:
        return []
    
    sources = []
    for ctx in context:
        if isinstance(ctx, dict) and "source" in ctx:
            sources.append(ctx["source"])
    
    return list(set(sources))  # Remove duplicates
