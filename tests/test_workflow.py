"""Test suite for workflow nodes and intelligent routing."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestIntelligentRouter:
    """Tests for intelligent routing logic."""
    
    @pytest.mark.asyncio
    async def test_route_finance_qa_query(self):
        """Test routing a general finance Q&A question."""
        from src.workflow.intelligent_router import intelligent_route_query
        
        with patch("src.workflow.intelligent_router._get_llm") as mock_llm_factory:
            mock_llm = AsyncMock()
            mock_llm_factory.return_value = mock_llm
            
            # Mock LLM response
            mock_response = MagicMock()
            mock_response.content = "AGENT|finance_qa|0.9|User asking general financial question"
            mock_llm.ainvoke.return_value = mock_response
            
            agent, reason, confidence = await intelligent_route_query("What is a stock?")
            
            assert agent in ["finance_qa", "market", "portfolio", "goal_planning", "news", "tax"]
            assert 0.0 <= confidence <= 1.0
            assert len(reason) > 0
    
    @pytest.mark.asyncio
    async def test_route_market_query(self):
        """Test routing a market data query."""
        from src.workflow.intelligent_router import intelligent_route_query
        
        with patch("src.workflow.intelligent_router._get_llm") as mock_llm_factory:
            mock_llm = AsyncMock()
            mock_llm_factory.return_value = mock_llm
            
            mock_response = MagicMock()
            mock_response.content = "AGENT|market|0.95|User asking about stock prices"
            mock_llm.ainvoke.return_value = mock_response
            
            agent, reason, confidence = await intelligent_route_query("What is AAPL trading at?")
            
            assert agent in ["market", "finance_qa", "portfolio", "goal_planning", "news", "tax"]
            assert confidence >= 0.0
    
    @pytest.mark.asyncio
    async def test_route_portfolio_query(self):
        """Test routing a portfolio analysis query."""
        from src.workflow.intelligent_router import intelligent_route_query
        
        with patch("src.workflow.intelligent_router._get_llm") as mock_llm_factory:
            mock_llm = AsyncMock()
            mock_llm_factory.return_value = mock_llm
            
            mock_response = MagicMock()
            mock_response.content = "AGENT|portfolio|0.88|User asking about portfolio"
            mock_llm.ainvoke.return_value = mock_response
            
            agent, reason, confidence = await intelligent_route_query("Should I rebalance my portfolio?")
            
            assert agent is not None
            assert isinstance(confidence, float)
    
    @pytest.mark.asyncio
    async def test_route_fallback_no_llm(self):
        """Test fallback routing when no LLM available."""
        from src.workflow.intelligent_router import intelligent_route_query
        
        with patch("src.workflow.intelligent_router._get_llm") as mock_llm_factory:
            mock_llm_factory.return_value = None  # No LLM
            
            agent, reason, confidence = await intelligent_route_query("Any question")
            
            assert agent == "finance_qa"  # Should default to finance_qa
            assert confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_router_valid_agent_names(self):
        """Test router only returns valid agent names."""
        from src.workflow.intelligent_router import intelligent_route_query
        
        valid_agents = ["finance_qa", "portfolio", "market", "goal_planning", "news", "tax"]
        
        test_queries = [
            "What is a stock?",
            "Analyze my portfolio",
            "What is AAPL price?",
            "Help me plan for retirement",
            "Tell me the news",
            "Explain capital gains tax",
        ]
        
        with patch("src.workflow.intelligent_router._get_llm") as mock_llm_factory:
            mock_llm = AsyncMock()
            mock_llm_factory.return_value = mock_llm
            
            for query in test_queries:
                mock_response = MagicMock()
                mock_response.content = f"AGENT|finance_qa|0.7|Routing {query}"
                mock_llm.ainvoke.return_value = mock_response
                
                agent, _, _ = await intelligent_route_query(query)
                assert agent in valid_agents


class TestWorkflowNodes:
    """Tests for workflow processing nodes."""
    
    @pytest.mark.asyncio
    async def test_router_node(self):
        """Test router node."""
        from src.workflow.langgraph_nodes import router_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "What is a stock?",
            "agent": "",
            "reason": "",
        }
        
        with patch("src.workflow.langgraph_nodes.intelligent_route_query") as mock_route:
            mock_route.return_value = ("finance_qa", "General Q&A", 0.9)
            
            result = await router_node(state)
            
            assert result["agent"] == "finance_qa"
            assert result["reason"] == "General Q&A"
            assert result["routing_confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_router_node_short_circuits_greeting(self):
        """A simple greeting should stay in the friendly general-chat path."""
        from src.workflow.langgraph_nodes import router_node
        from src.workflow.state import WorkflowState

        state: WorkflowState = {
            "message": "Hi",
            "agent": "",
            "reason": "",
        }

        result = await router_node(state)

        assert result["agent"] == "llm"
        assert result["is_greeting"] is True
        assert result["routing_confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_router_node_short_circuits_obvious_quote_request(self):
        """Obvious quote requests should route directly to market without LLM classification."""
        from src.workflow.langgraph_nodes import router_node
        from src.workflow.state import WorkflowState

        state: WorkflowState = {
            "message": "What is AAPL trading at?",
            "agent": "",
            "reason": "",
        }

        with patch("src.workflow.langgraph_nodes._get_llm") as mock_llm_factory:
            mock_llm_factory.side_effect = AssertionError("LLM should not be called for obvious quote requests")

            result = await router_node(state)

            assert result["agent"] == "data_enrichment"
            assert result["execution_mode"] == "fast"
            assert "market" in result["reason"].lower()
            assert result["routing_confidence"] >= 0.6
    
    @pytest.mark.asyncio
    async def test_rag_node(self):
        """Test RAG retrieval node."""
        from src.workflow.langgraph_nodes import rag_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "What is diversification?",
            "agent": "finance_qa",
            "reason": "",
        }
        
        with patch("src.workflow.langgraph_nodes.retrieve_context") as mock_retrieve:
            mock_retrieve.return_value = [
                {"text": "Diversification spreads risk", "source": "knowledge_base.md"}
            ]
            
            result = await rag_node(state)
            
            assert "context" in result
            assert len(result["context"]) > 0
    
    @pytest.mark.asyncio
    async def test_data_enrichment_node_market(self):
        """Test data enrichment node for market agent."""
        from src.workflow.langgraph_nodes import data_enrichment_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "What is AAPL price?",
            "agent": "market",
            "reason": "Market query",
        }
        
        with patch("src.data.market_service.get_quote_for_message") as mock_market:
            mock_market.return_value = "AAPL: $150.00 (+1.00%)"
            
            result = await data_enrichment_node(state)
            
            assert result["agent"] == "market"

    @pytest.mark.asyncio
    async def test_llm_node_passes_market_data_for_data_enrichment_route(self):
        """The chat workflow must pass market data even when the route label is data_enrichment."""
        from src.workflow.langgraph_nodes import llm_node
        from src.workflow.state import WorkflowState

        state: WorkflowState = {
            "message": "What is AAPL stock price?",
            "agent": "data_enrichment",
            "reason": "Direct market route",
            "market_data": "AAPL: $214.56 (+0.52%)",
            "context": [],
            "attempt_count": 0,
        }

        with patch("src.agents.market.MarketAgent") as mock_market_agent:
            mock_agent = AsyncMock()
            mock_agent.generate_response.return_value = "AAPL: $214.56 (+0.52%)"
            mock_market_agent.return_value = mock_agent

            result = await llm_node(state)

            assert result["response"] == "AAPL: $214.56 (+0.52%)"
            mock_agent.generate_response.assert_called_once()
            call_kwargs = mock_agent.generate_response.call_args.kwargs
            assert call_kwargs["additional_data"]["market_data"] == "AAPL: $214.56 (+0.52%)"
            assert "market_data" in result
    
    @pytest.mark.asyncio
    async def test_data_enrichment_node_portfolio(self):
        """Test data enrichment node for portfolio agent."""
        from src.workflow.langgraph_nodes import data_enrichment_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "Analyze my portfolio",
            "agent": "portfolio",
            "reason": "Portfolio query",
        }
        
        with patch("src.data.portfolio_service.get_user_portfolio") as mock_portfolio:
            mock_portfolio.return_value = {
                "holdings": [{"symbol": "AAPL", "quantity": 10}]
            }
            
            result = await data_enrichment_node(state)
            
            assert result["agent"] == "portfolio"
            assert "portfolio_data" in result
    
    @pytest.mark.asyncio
    async def test_llm_node_generates_response(self, mock_llm):
        """Test LLM node generates response."""
        from src.workflow.langgraph_nodes import llm_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "What is a stock?",
            "agent": "finance_qa",
            "reason": "Education",
            "context": [{"text": "A stock is ownership", "source": "test"}],
        }
        
        with patch("src.workflow.langgraph_nodes.FinanceQAAgent") as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.generate_response.return_value = "A stock represents ownership in a company."
            mock_agent_class.return_value = mock_agent
            
            result = await llm_node(state)
            
            assert "response" in result
            assert len(result["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_llm_node_error_handling(self):
        """Test LLM node handles errors gracefully."""
        from src.workflow.langgraph_nodes import llm_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "Any question",
            "agent": "finance_qa",
            "reason": "Test",
        }
        
        with patch("src.workflow.langgraph_nodes.FinanceQAAgent") as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.generate_response.side_effect = Exception("API Error")
            mock_agent_class.return_value = mock_agent
            
            result = await llm_node(state)
            
            # Should have fallback response
            assert "response" in result
            assert len(result["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_response_formatter_node(self):
        """Test response formatter node adds sources."""
        from src.workflow.langgraph_nodes import response_formatter_node
        from src.workflow.state import WorkflowState
        
        state: WorkflowState = {
            "message": "What is a stock?",
            "agent": "finance_qa",
            "reason": "",
            "response": "A stock is ownership in a company.",
            "context": [
                {"source": "investopedia.com"},
                {"source": "sec.gov"},
            ],
        }
        
        result = await response_formatter_node(state)
        
        assert "sources" in result
        assert len(result["sources"]) == 2


class TestWorkflowIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self):
        """Test complete workflow from message to response."""
        from src.workflow.langgraph_workflow import run_langgraph_workflow
        
        # This test may take time as it runs the full pipeline
        with patch("src.workflow.intelligent_router.intelligent_route_query") as mock_route:
            with patch("src.rag.retriever.retrieve_context") as mock_rag:
                mock_route.return_value = ("finance_qa", "Q&A", 0.9)
                mock_rag.return_value = [{"text": "Stocks represent ownership", "source": "kb"}]
                
                # Mock the agent
                with patch("src.agents.finance_qa.FinanceQAAgent") as mock_agent_class:
                    mock_agent = AsyncMock()
                    mock_agent.generate_response.return_value = "A stock is ownership in a company."
                    mock_agent_class.return_value = mock_agent
                    
                    result = await run_langgraph_workflow("What is a stock?")
                    
                    assert "response" in result
                    assert result["agent"] == "finance_qa"
                    assert result["routing_confidence"] == 0.9
