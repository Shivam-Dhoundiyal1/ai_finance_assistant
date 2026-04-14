"""Finance Q&A Agent: general financial education queries."""
from typing import Any

from src.agents.base import BaseAgent


class FinanceQAAgent(BaseAgent):
    name = "finance_qa"
    description = "Handles general financial education queries, definitions, and concepts."

    def get_agent_temperature(self) -> float:
        return 0.2  # Lower temperature for factual, educational content

    def get_agent_max_tokens(self) -> int:
        return 1200  # More tokens for detailed explanations

    def get_system_prompt(self) -> str:
        return (
            "You are a knowledgeable financial education expert. "
            "Your role is to explain financial concepts clearly and accurately. "
            "Focus on educational content that helps users understand finance better. "
            "Use analogies and simple language when possible. "
            "Always include a brief disclaimer that this is for educational purposes only "
            "and users should consult professionals for personalized advice."
        )

    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate educational financial response using agent's LLM."""
        return await self.generate_response(message, context)
