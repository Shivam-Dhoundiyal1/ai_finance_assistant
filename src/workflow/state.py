"""State for the workflow graph."""
from typing import Annotated, Any, TypedDict

from typing_extensions import NotRequired


class WorkflowState(TypedDict):
    message: str
    agent: str
    reason: str
    is_greeting: NotRequired[bool]
    routing_confidence: NotRequired[float]
    attempt_count: NotRequired[int]
    max_attempts: NotRequired[int]
    execution_trace: NotRequired[list[dict[str, Any]]]
    critic_status: NotRequired[str]
    critic_reason: NotRequired[str]
    retry_reason: NotRequired[str]
    fallback_agent: NotRequired[str]
    context: NotRequired[list[dict[str, Any]]]
    market_data: NotRequired[dict[str, Any]]
    portfolio_data: NotRequired[dict[str, Any]]
    response: NotRequired[str]
    sources: NotRequired[list[str]]
    error: NotRequired[str]
