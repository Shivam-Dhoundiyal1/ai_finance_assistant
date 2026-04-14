"""News Synthesizer Agent: summarizes and contextualizes financial news."""
from typing import Any

from src.agents.base import BaseAgent


class NewsSynthesizerAgent(BaseAgent):
    name = "news"
    description = "Summarizes financial news and current events."

    def get_agent_temperature(self) -> float:
        return 0.3  # Low temperature for factual news

    def get_agent_max_tokens(self) -> int:
        return 800  # Concise news summaries

    def get_system_prompt(self) -> str:
        return (
            "You are a financial news analyst specializing in market news synthesis. "
            "You provide accurate, timely information about financial markets, "
            "economic events, and company news. Always cite sources when possible "
            "and distinguish between facts and analysis. Focus on market-relevant news "
            "that would impact investment decisions. Be objective and balanced in your reporting."
        )

    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        # Generate news-focused response using the agent's LLM
        return await self.generate_response(message, context)
