"""Market Agent: handles market data, stock quotes, and market analysis."""
from typing import Any

from src.agents.base import BaseAgent


class MarketAgent(BaseAgent):
    name = "market"
    description = "Handles stock quotes, market data, and market analysis queries."

    def get_agent_temperature(self) -> float:
        return 0.1  # Very low temperature for factual market data

    def get_agent_max_tokens(self) -> int:
        return 800  # Concise market-focused responses

    def get_system_prompt(self) -> str:
        return (
            "You are a market data analyst specializing in stock prices and market information. "
            "Provide accurate, factual information about stock quotes, market trends, and trading data. "
            "Focus on explaining what the data means for investors in educational terms. "
            "Always include the disclaimer that market data is for informational purposes only "
            "and not investment advice. Be precise with numbers and dates."
        )

    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate market-focused response using agent's LLM."""
        # Extract market data if available
        market_data = kwargs.get("market_data")
        additional_data = {"market_data": market_data} if market_data else None
        
        return await self.generate_response(message, context, additional_data)
