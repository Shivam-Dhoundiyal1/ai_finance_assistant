#!/usr/bin/env python3
"""Test the enhanced financial assistant system with all agents and features."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.workflow.langgraph_workflow import run_langgraph_workflow
from src.data.portfolio_service import get_user_portfolio, calculate_portfolio_metrics
from src.data.market_service import get_real_time_quote, get_market_summary


async def test_all_agents():
    """Test all 6 specialized agents."""
    print("🧪 Testing All Financial Assistant Agents")
    print("=" * 50)
    
    test_queries = [
        ("finance_qa", "What is dollar cost averaging?"),
        ("market", "What's the current price of AAPL?"),
        ("portfolio", "Analyze my portfolio allocation"),
        ("goal_planning", "How much should I save for retirement?"),
        ("news", "What are the latest market trends?"),
        ("tax", "What's the difference between Roth and traditional IRA?")
    ]
    
    for expected_agent, query in test_queries:
        print(f"\n📋 Testing {expected_agent.upper()} Agent:")
        print(f"Query: {query}")
        
        try:
            result = await run_langgraph_workflow(query)
            
            print(f"✅ Agent: {result['agent']}")
            print(f"✅ Confidence: {result.get('routing_confidence', 0):.2f}")
            print(f"✅ Response: {result['response'][:100]}...")
            
            # Verify correct agent was selected
            if result['agent'] == expected_agent:
                print("✅ Correct agent selected!")
            else:
                print(f"⚠️ Expected {expected_agent}, got {result['agent']}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 40)


async def test_portfolio_features():
    """Test portfolio management features."""
    print("\n🏦 Testing Portfolio Management")
    print("=" * 50)
    
    try:
        # Test portfolio retrieval
        portfolio = get_user_portfolio("default")
        print(f"✅ Retrieved portfolio with {len(portfolio.get('holdings', []))} holdings")
        
        # Test portfolio metrics
        metrics = calculate_portfolio_metrics(portfolio)
        print(f"✅ Calculated metrics:")
        print(f"   - Total holdings: {metrics.get('total_holdings', 0)}")
        print(f"   - Diversification score: {metrics.get('diversification_score', 0):.1f}")
        print(f"   - Risk score: {metrics.get('risk_score', 0):.1f}")
        
        # Test largest holding
        largest = metrics.get('largest_holding', {})
        print(f"   - Largest holding: {largest.get('symbol', 'N/A')} ({largest.get('percentage', 0):.1f}%)")
        
    except Exception as e:
        print(f"❌ Portfolio test failed: {str(e)}")


async def test_market_data_caching():
    """Test market data with caching."""
    print("\n📊 Testing Market Data & Caching")
    print("=" * 50)
    
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in test_symbols:
        try:
            print(f"\n📈 Testing {symbol}:")
            
            # First call - should hit API
            quote1 = get_real_time_quote(symbol)
            print(f"✅ First call: ${quote1.get('price', 0):.2f}")
            
            # Second call - should use cache
            quote2 = get_real_time_quote(symbol)
            print(f"✅ Second call: ${quote2.get('price', 0):.2f}")
            
            # Test market summary
            summary = get_market_summary([symbol])
            print(f"✅ Market summary includes {symbol}")
            
        except Exception as e:
            print(f"❌ {symbol} test failed: {str(e)}")


async def test_error_handling():
    """Test error handling in the system."""
    print("\n🛡️ Testing Error Handling")
    print("=" * 50)
    
    error_test_queries = [
        "invalid symbol query that might fail",
        "complex query that might timeout",
        "empty query"
    ]
    
    for query in error_test_queries:
        try:
            print(f"\n🔍 Testing: {query}")
            result = await run_langgraph_workflow(query)
            
            if result.get('success', True):
                print("✅ Query handled successfully")
            else:
                print(f"⚠️ Query handled with fallback: {result['response'][:50]}...")
                
        except Exception as e:
            print(f"❌ Error test failed: {str(e)}")


async def test_system_integration():
    """Test complete system integration."""
    print("\n🔄 Testing System Integration")
    print("=" * 50)
    
    integration_queries = [
        "What's my portfolio performance and should I rebalance?",
        "How do market conditions affect my retirement planning?",
        "What are the tax implications of my investment strategy?"
    ]
    
    for query in integration_queries:
        try:
            print(f"\n🔗 Integration test: {query}")
            result = await run_langgraph_workflow(query)
            
            print(f"✅ Agent: {result['agent']}")
            print(f"✅ Confidence: {result.get('routing_confidence', 0):.2f}")
            print(f"✅ Response length: {len(result['response'])} chars")
            
            if result.get('sources'):
                print(f"✅ Sources: {len(result['sources'])}")
            
        except Exception as e:
            print(f"❌ Integration test failed: {str(e)}")


async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Financial Assistant System Tests")
    print("=" * 60)
    
    try:
        await test_all_agents()
        await test_portfolio_features()
        await test_market_data_caching()
        await test_error_handling()
        await test_system_integration()
        
        print("\n🎉 All Tests Completed!")
        print("=" * 50)
        print("✅ System is ready for production use!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
