"""
Conversation Context Manager for Multi-turn Chat

Maintains conversation history and context across multiple exchanges,
improving response quality and continuity.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import json

class MessageRole(str, Enum):
    """Chat message role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class ChatMessage:
    """Single chat message with metadata"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    source_documents: List[str] = field(default_factory=list)  # RAG sources
    confidence_score: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "sources": self.source_documents,
            "confidence": self.confidence_score
        }

@dataclass
class ConversationContext:
    """
    Maintains conversation history and context for multi-turn chats
    
    Features:
    - Message history with timestamps
    - User financial profile tracking
    - Detected intents and topics
    - Session metadata
    """
    conversation_id: str
    user_id: Optional[str] = None
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Context state
    detected_intent: Optional[str] = None  # "portfolio_analysis", "tax_planning", etc
    detected_topics: List[str] = field(default_factory=list)  # ["stocks", "retirement", "tax"]
    user_profile: dict = field(default_factory=dict)  # {"age": 35, "risk_tolerance": "moderate"}
    session_metadata: dict = field(default_factory=dict)
    
    # Configuration
    max_history: int = 10  # Keep last N messages for context window
    context_window_tokens: int = 4000
    
    def add_message(self, role: MessageRole, content: str, 
                   sources: Optional[List[str]] = None,
                   confidence: Optional[float] = None) -> None:
        """Add a message to conversation history"""
        message = ChatMessage(
            role=role,
            content=content,
            source_documents=sources or [],
            confidence_score=confidence
        )
        self.messages.append(message)
        self.last_updated = datetime.now()
        
        # Keep only recent messages in active history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_conversation_summary(self) -> str:
        """Generate concise summary of conversation for context"""
        if not self.messages:
            return ""
        
        # Create summary from key messages
        summary_parts = []
        
        # Add intent if detected
        if self.detected_intent:
            summary_parts.append(f"Intent: {self.detected_intent}")
        
        # Add detected topics
        if self.detected_topics:
            summary_parts.append(f"Topics: {', '.join(self.detected_topics)}")
        
        # Add recent user questions (last 3)
        recent_questions = [
            m.content for m in self.messages 
            if m.role == MessageRole.USER
        ][-3:]
        
        if recent_questions:
            summary_parts.append(f"Recent questions: {'; '.join(recent_questions[:2])}")
        
        return "\n".join(summary_parts)
    
    def get_system_prompt_injection(self) -> str:
        """Generate system prompt with conversation context"""
        if not self.messages:
            return ""
        
        # Build context for the LLM
        context_parts = []
        
        if self.user_profile:
            profile_str = ", ".join([f"{k}: {v}" for k, v in self.user_profile.items()])
            context_parts.append(f"User Profile: {profile_str}")
        
        if self.detected_topics:
            context_parts.append(f"Conversation Topics: {', '.join(self.detected_topics)}")
        
        if self.detected_intent:
            context_parts.append(f"Detected Intent: {self.detected_intent}")
        
        # Add relevant history (last 3 exchanges)
        recent_exchanges = []
        for i in range(max(0, len(self.messages) - 6), len(self.messages), 2):
            if i + 1 < len(self.messages):
                recent_exchanges.append(
                    f"User: {self.messages[i].content}\n"
                    f"Assistant: {self.messages[i+1].content}"
                )
        
        if recent_exchanges:
            context_parts.append(f"Recent Conversation:\n" + "\n\n".join(recent_exchanges))
        
        return "\n\n".join(context_parts)
    
    def extract_user_profile_updates(self, message: str) -> dict:
        """Extract user profile information from messages"""
        updates = {}
        
        # Simple keyword-based extraction (could be enhanced with NLP)
        keywords = {
            "age": ["i'm ", "i am ", "year old"],
            "risk_tolerance": ["risk", "aggressive", "conservative", "moderate"],
            "investment_horizon": ["years", "timeline", "retirement"],
        }
        
        message_lower = message.lower()
        for field, terms in keywords.items():
            for term in terms:
                if term in message_lower:
                    updates[field] = True  # Mark as mentioned
        
        return updates
    
    def to_dict(self) -> dict:
        """Serialize conversation context"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "detected_intent": self.detected_intent,
            "detected_topics": self.detected_topics,
            "user_profile": self.user_profile,
            "session_metadata": self.session_metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationContext':
        """Deserialize conversation context"""
        context = cls(
            conversation_id=data['conversation_id'],
            user_id=data.get('user_id'),
            detected_intent=data.get('detected_intent'),
            detected_topics=data.get('detected_topics', []),
            user_profile=data.get('user_profile', {}),
            session_metadata=data.get('session_metadata', {})
        )
        
        # Reconstruct messages
        for msg_data in data.get('messages', []):
            msg = ChatMessage(
                role=MessageRole(msg_data['role']),
                content=msg_data['content'],
                timestamp=datetime.fromisoformat(msg_data['timestamp']),
                source_documents=msg_data.get('sources', []),
                confidence_score=msg_data.get('confidence')
            )
            context.messages.append(msg)
        
        return context

class ConversationStore:
    """In-memory store for conversation contexts (can be extended to use Redis/DB)"""
    
    def __init__(self):
        self.conversations: dict[str, ConversationContext] = {}
    
    def get_or_create(self, conversation_id: str, user_id: Optional[str] = None) -> ConversationContext:
        """Get existing conversation or create new one"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id
            )
        return self.conversations[conversation_id]
    
    def save(self, context: ConversationContext) -> None:
        """Save conversation context"""
        self.conversations[context.conversation_id] = context
    
    def delete(self, conversation_id: str) -> None:
        """Delete conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_user_conversations(self, user_id: str) -> List[ConversationContext]:
        """Get all conversations for a user"""
        return [
            c for c in self.conversations.values()
            if c.user_id == user_id
        ]

# Global conversation store instance
_conversation_store = ConversationStore()

def get_conversation_store() -> ConversationStore:
    """Get the global conversation store"""
    return _conversation_store
