"""Goal Planning Agent: financial goal setting and planning."""
from typing import Any

from src.agents.base import BaseAgent


class GoalPlanningAgent(BaseAgent):
    name = "goal_planning"
    description = "Assists with financial goals, retirement, savings targets, and risk tolerance."

    def get_agent_temperature(self) -> float:
        return 0.4  # Moderate temperature for planning flexibility

    def get_agent_max_tokens(self) -> int:
        return 1000  # Detailed planning responses

    def get_system_prompt(self) -> str:
        return (
            "You are a financial planning expert specializing in goal setting, retirement planning, "
            "and investment strategy. You help users define financial goals, create savings plans, "
            "assess risk tolerance, and plan for major life events. Topics include retirement "
            "planning, emergency funds, education savings, home buying, and investment timelines. "
            "Always provide educational guidance with appropriate disclaimers that this is not "
            "personalized financial advice. Encourage users to consider their unique circumstances "
            "and consult financial professionals for major decisions."
        )

    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        # Generate planning-focused response using the agent's LLM
        return await self.generate_response(message, context)
