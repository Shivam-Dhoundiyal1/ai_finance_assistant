from src.agents.base import BaseAgent
from src.agents.finance_qa import FinanceQAAgent
from src.agents.portfolio import PortfolioAnalysisAgent
from src.agents.market import MarketAgent
from src.agents.goal_planning import GoalPlanningAgent
from src.agents.news import NewsSynthesizerAgent
from src.agents.tax import TaxEducationAgent

AGENTS = {
    "finance_qa": FinanceQAAgent,
    "portfolio": PortfolioAnalysisAgent,
    "market": MarketAgent,
    "goal_planning": GoalPlanningAgent,
    "news": NewsSynthesizerAgent,
    "tax": TaxEducationAgent,
}

__all__ = [
    "BaseAgent",
    "FinanceQAAgent",
    "PortfolioAnalysisAgent",
    "MarketAnalysisAgent",
    "GoalPlanningAgent",
    "NewsSynthesizerAgent",
    "TaxEducationAgent",
    "AGENTS",
]
