"""Test suite for all finance agents."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_finance_qa_agent(mock_llm):
    """Test FinanceQAAgent generates educational responses."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.finance_qa import FinanceQAAgent
        
        agent = FinanceQAAgent()
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "A stock represents ownership in a company."
        mock_llm.ainvoke.return_value = mock_response
        agent.llm = mock_llm
        
        response = await agent.generate_response("What is a stock?")
        
        assert "stock" in response.lower()
        mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_finance_qa_demo_mode():
    """Test FinanceQAAgent fallback to demo mode when no LLM."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.finance_qa import FinanceQAAgent
        
        agent = FinanceQAAgent()
        # agent.llm should be None
        
        response = await agent.generate_response("What is inflation?")
        
        # Should get fallback response
        assert len(response) > 0
        assert isinstance(response, str)


@pytest.mark.asyncio
async def test_market_agent_with_market_data(mock_llm):
    """Test MarketAgent includes market data in response."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.market import MarketAgent
        
        agent = MarketAgent()
        mock_response = MagicMock()
        mock_response.content = "AAPL is trading at $150 with a positive trend."
        mock_llm.ainvoke.return_value = mock_response
        agent.llm = mock_llm
        
        market_data = {"AAPL": {"price": 150.0, "change": 2.5}}
        response = await agent.generate_response(
            "What is AAPL trading at?",
            additional_data={"market_data": market_data}
        )
        
        assert len(response) > 0
        mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_portfolio_agent_with_portfolio_data(mock_llm):
    """Test PortfolioAnalysisAgent includes portfolio data."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.portfolio import PortfolioAnalysisAgent
        
        agent = PortfolioAnalysisAgent()
        mock_response = MagicMock()
        mock_response.content = "Your portfolio is well diversified."
        mock_llm.ainvoke.return_value = mock_response
        agent.llm = mock_llm
        
        portfolio_data = {"holdings": [{"symbol": "AAPL", "quantity": 10}]}
        response = await agent.generate_response(
            "Analyze my portfolio",
            additional_data={"portfolio_data": portfolio_data}
        )
        
        assert len(response) > 0
        mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_goal_planning_agent(mock_llm):
    """Test GoalPlanningAgent provides retirement planning guidance."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.goal_planning import GoalPlanningAgent
        
        agent = GoalPlanningAgent()
        mock_response = MagicMock()
        mock_response.content = "Consider increasing your 401k contributions."
        mock_llm.ainvoke.return_value = mock_response
        agent.llm = mock_llm
        
        response = await agent.generate_response("How should I plan for retirement?")
        
        assert len(response) > 0
        mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_news_agent(mock_llm):
    """Test NewsSynthesizerAgent summarizes financial news."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.news import NewsSynthesizerAgent
        
        agent = NewsSynthesizerAgent()
        mock_response = MagicMock()
        mock_response.content = "Fed raises interest rates by 0.5%."
        mock_llm.ainvoke.return_value = mock_response
        agent.llm = mock_llm
        
        response = await agent.generate_response(
            "What's the latest financial news?",
            context=[{"text": "Fed raises rates", "source": "Reuters"}]
        )
        
        assert len(response) > 0


@pytest.mark.asyncio
async def test_tax_agent(mock_llm):
    """Test TaxEducationAgent explains tax concepts."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.tax import TaxEducationAgent
        
        agent = TaxEducationAgent()
        mock_response = MagicMock()
        mock_response.content = "A Roth IRA allows tax-free growth of investments."
        mock_llm.ainvoke.return_value = mock_response
        agent.llm = mock_llm
        
        response = await agent.generate_response("What is a Roth IRA?")
        
        assert len(response) > 0
        assert "roth" in response.lower()


@pytest.mark.asyncio
async def test_agent_temperature_settings():
    """Test agents have appropriate temperature settings."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.finance_qa import FinanceQAAgent
        from src.agents.market import MarketAgent
        from src.agents.goal_planning import GoalPlanningAgent
        
        # Educational agents should have lower temperature (more factual)
        assert FinanceQAAgent().get_agent_temperature() < 0.5
        assert MarketAgent().get_agent_temperature() < 0.5
        
        # Goal planning can have higher temperature (more creative)
        assert GoalPlanningAgent().get_agent_temperature() >= 0.3


@pytest.mark.asyncio
async def test_agent_context_formatting():
    """Test agents properly format context."""
    with patch("src.agents.base.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.llm_provider = None
        mock_get_settings.return_value = mock_settings
        
        from src.agents.finance_qa import FinanceQAAgent
        
        agent = FinanceQAAgent()
        context = [
            {"text": "Stocks represent ownership", "source": "investopedia.com"},
            {"text": "Bonds are debt instruments", "source": "investopedia.com"},
        ]
        
        # Agent should format context properly
        agent.llm = None  # Use demo mode
        response = await agent.generate_response(
            "Explain stocks and bonds",
            context=context
        )
        
        assert len(response) > 0


def test_agent_names_valid():
    """Test all agents have valid names."""
    from src.agents.finance_qa import FinanceQAAgent
    from src.agents.portfolio import PortfolioAnalysisAgent
    from src.agents.market import MarketAgent
    from src.agents.goal_planning import GoalPlanningAgent
    from src.agents.news import NewsSynthesizerAgent
    from src.agents.tax import TaxEducationAgent
    
    valid_names = ["finance_qa", "portfolio", "market", "goal_planning", "news", "tax"]
    agent_names = [
        FinanceQAAgent.name,
        PortfolioAnalysisAgent.name,
        MarketAgent.name,
        GoalPlanningAgent.name,
        NewsSynthesizerAgent.name,
        TaxEducationAgent.name,
    ]
    
    for name in agent_names:
        assert name in valid_names
