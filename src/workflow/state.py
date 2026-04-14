"""State for the workflow graph."""
from typing import Annotated, Any, TypedDict

from typing_extensions import NotRequired


class WorkflowState(TypedDict):
    message: str
    agent: str
    reason: str
    routing_confidence: NotRequired[float]
    context: NotRequired[list[dict[str, Any]]]
    market_data: NotRequired[dict[str, Any]]
    portfolio_data: NotRequired[dict[str, Any]]
    response: NotRequired[str]
    sources: NotRequired[list[str]]
