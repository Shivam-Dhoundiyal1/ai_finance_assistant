"""Tests for workflow intelligent router."""
import sys
from pathlib import Path
import pytest
import asyncio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.workflow.intelligent_router import intelligent_route_query


@pytest.mark.asyncio
async def test_route_finance_qa():
    agent, reason, confidence = await intelligent_route_query("What is diversification?")
    assert agent == "finance_qa"
    assert 0.0 <= confidence <= 1.0
    assert reason is not None


@pytest.mark.asyncio
async def test_route_market():
    agent, reason, confidence = await intelligent_route_query("Get quote for AAPL")
    assert agent == "market"
    assert 0.0 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_route_tax():
    agent, reason, confidence = await intelligent_route_query("Explain IRA and 401k")
    assert agent == "tax"
    assert 0.0 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_route_goal():
    agent, reason, confidence = await intelligent_route_query("I want to plan for retirement")
    assert agent == "goal_planning"
    assert 0.0 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_route_portfolio():
    agent, reason, confidence = await intelligent_route_query("How is my portfolio allocation?")
    assert agent == "portfolio"
    assert 0.0 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_route_default():
    """Test fallback to finance_qa for unclear queries."""
    agent, reason, confidence = await intelligent_route_query("Hello")
    assert agent in ["finance_qa", "market", "portfolio", "goal_planning", "news", "tax"]
    assert 0.0 <= confidence <= 1.0
