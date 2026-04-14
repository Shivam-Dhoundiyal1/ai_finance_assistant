"""Base agent interface; all agents produce a response from message + optional context."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.core.config import get_settings


class BaseAgent(ABC):
    """Base class for all finance agents."""

    name: str = "base"
    description: str = ""
    
    def __init__(self):
        self.llm = self._get_agent_llm()
    
    def _get_agent_llm(self):
        """Return configured LLM for this agent."""
        s = get_settings()
        if s.llm_provider == "openai" and s.openai_api_key:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=s.llm_model,
                temperature=self.get_agent_temperature(),
                max_tokens=self.get_agent_max_tokens(),
                api_key=s.openai_api_key,
            )
        if s.llm_provider == "gemini" and s.gemini_api_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=s.llm_model or "gemini-pro",
                temperature=self.get_agent_temperature(),
                max_tokens=self.get_agent_max_tokens(),
                google_api_key=s.gemini_api_key,
            )
        return None
    
    def get_agent_temperature(self) -> float:
        """Override to provide agent-specific temperature."""
        return 0.3
    
    def get_agent_max_tokens(self) -> int:
        """Override to provide agent-specific token limit."""
        return 1024
    
    def get_system_prompt(self) -> str:
        """Override to provide agent-specific system prompt."""
        return (
            "You are a helpful financial education assistant. "
            "Provide clear, educational responses about financial topics. "
            "Always include a disclaimer that this is for educational purposes only."
        )
    
    async def generate_response(
        self,
        message: str,
        context: List[Dict[str, Any]] | None = None,
        additional_data: Dict[str, Any] | None = None,
    ) -> str:
        """
        Generate response using the agent's LLM with context and additional data.
        Falls back to demo mode if LLM is not configured.
        """
        if not self.llm:
            # Demo/fallback responses when no LLM is configured
            return self._generate_demo_response(message, context, additional_data)
        
        # Build context-aware prompt
        context_text = self._format_context(context) if context else "No specific context available."
        
        user_content = f"""
User question: {message}

Relevant context: {context_text}
"""
        
        # Add agent-specific additional data
        if additional_data:
            for key, value in additional_data.items():
                if value:
                    user_content += f"\n{key.replace('_', ' ').title()}: {value}"
        
        user_content += "\n\nProvide a helpful, educational response based on the above information."
        
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=self.get_system_prompt()),
                HumanMessage(content=user_content),
            ]
            
            result = await self.llm.ainvoke(messages)
            return result.content if hasattr(result, "content") else str(result)
            
        except Exception as e:
            return f"I encountered an error generating a response: {e}"
    
    def _generate_demo_response(
        self,
        message: str,
        context: List[Dict[str, Any]] | None = None,
        additional_data: Dict[str, Any] | None = None,
    ) -> str:
        """Generate a demo response when no LLM is configured."""
        return (
            f"[Demo Mode] I'm responding to your question about: {message}. "
            "This is a demonstration response since no LLM is configured. "
            "In production, I would provide a detailed, intelligent response."
        )
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context for the agent."""
        if not context:
            return "(No retrieved documents)"
        
        parts = []
        for i, c in enumerate(context, 1):
            text = (c.get("text") or "").strip()
            src = c.get("source") or "Unknown"
            if text:
                parts.append(f"[{i}] {text}\nSource: {src}")
        
        return "\n\n".join(parts) if parts else "(No retrieved documents)"

    @abstractmethod
    async def run(
        self,
        message: str,
        context: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate response. context is RAG chunks when applicable."""
        pass
