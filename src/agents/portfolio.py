"""Portfolio Analysis Agent: reviews and analyzes user portfolios."""
from typing import Any

from src.agents.base import BaseAgent


class PortfolioAnalysisAgent(BaseAgent):
    name = "portfolio"
    description = "Analyzes portfolio allocation, diversification, and suggests rebalancing."

    def get_agent_temperature(self) -> float:
        return 0.2  # Slightly higher for portfolio management

    def get_agent_max_tokens(self) -> int:
        return 1000  # More detailed portfolio analysis

    def get_system_prompt(self) -> str:
        return (
            "You are a portfolio management specialist. "
            "You can help users analyze their portfolio, understand allocation, "
            "and provide educational insights about diversification and rebalancing. "
            "Always include educational disclaimers that portfolio analysis is for informational purposes "
            "and not investment advice. Focus on explaining concepts clearly and providing actionable insights."
        )

    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        # Extract portfolio data if provided
        portfolio_data = kwargs.get("portfolio_data")
        
        if portfolio_data:
            # Use real portfolio data for analysis
            return await self.generate_response(
                message, 
                context, 
                {"portfolio_data": portfolio_data}
            )
        else:
            # Use sample portfolio or general portfolio advice
            return await self.generate_response(message, context)
