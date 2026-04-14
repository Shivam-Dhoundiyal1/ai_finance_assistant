"""Quick test to verify settings are loaded."""
from src.core.config import get_settings

s = get_settings()
print(f"LLM Provider: {s.llm_provider}")
print(f"LLM Model: {s.llm_model}")
print(f"OpenAI API Key: {'Set' if s.openai_api_key else 'NOT SET'}")
print(f"Gemini API Key: {'Set' if s.gemini_api_key else 'NOT SET'}")

# Test LLM initialization
from src.agents.finance_qa import FinanceQAAgent

agent = FinanceQAAgent()
print(f"\nFinanceQA Agent LLM: {type(agent.llm).__name__ if agent.llm else 'NOT SET'}")
