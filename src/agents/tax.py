"""Tax Education Agent: tax concepts and account types."""
from typing import Any

from src.agents.base import BaseAgent


class TaxEducationAgent(BaseAgent):
    name = "tax"
    description = "Explains tax concepts, IRA, 401(k), Roth, capital gains, and withholding."

    def get_agent_temperature(self) -> float:
        return 0.2  # Low temperature for tax accuracy

    def get_agent_max_tokens(self) -> int:
        return 900  # Detailed tax explanations

    def get_system_prompt(self) -> str:
        return (
            "You are a tax education specialist providing clear, accurate information about "
            "tax concepts, retirement accounts, and investment taxation. You explain topics like "
            "IRAs, 401(k)s, Roth accounts, capital gains, dividends, and tax strategies. "
            "Always include appropriate disclaimers that tax information is educational and not "
            "professional tax advice. Encourage users to consult tax professionals for personal situations. "
            "Focus on US tax system and keep explanations accessible to non-experts."
        )

    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        # Generate tax-focused response using the agent's LLM
        return await self.generate_response(message, context)
