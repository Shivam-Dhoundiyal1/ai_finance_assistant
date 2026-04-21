"""
Enhanced Chat API with Conversation Context Support

Provides multi-turn conversation support with context persistence,
allowing the AI to maintain state across multiple user exchanges.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

from src.core.conversation_context import (
    ConversationContext, MessageRole, get_conversation_store
)

# API Models
class ChatMessageRequest(BaseModel):
    """User chat message request"""
    message: str = Field(..., description="User's chat message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn chats")
    user_id: Optional[str] = Field(None, description="User identifier")
    include_sources: bool = Field(True, description="Include RAG sources in response")

class ChatMessageResponse(BaseModel):
    """Chat API response"""
    response: str
    conversation_id: str
    message_id: str
    timestamp: datetime
    sources: List[str] = []
    confidence: float = 1.0
    thinking_process: Optional[str] = None
    conversation_summary: Optional[str] = None

class ConversationHistoryRequest(BaseModel):
    """Request conversation history"""
    conversation_id: str

class ConversationHistoryResponse(BaseModel):
    """Return conversation history"""
    conversation_id: str
    messages: List[dict]
    metadata: dict
    created_at: datetime
    last_updated: datetime

class ConversationDeleteRequest(BaseModel):
    """Delete a conversation"""
    conversation_id: str

# Initialize router
router = APIRouter(prefix="/api", tags=["chat"])

# Dependency to get conversation store
def get_store():
    return get_conversation_store()

@router.post("/chat", response_model=ChatMessageResponse)
async def chat(request: ChatMessageRequest, store = None):
    """
    Chat endpoint with conversation context support
    
    Features:
    - Multi-turn conversation support
    - Automatic context management
    - RAG-enhanced responses
    - Source tracking
    
    Args:
        request: ChatMessageRequest with message and optional conversation_id
    
    Returns:
        ChatMessageResponse with response, sources, and conversation tracking
    """
    if store is None:
        store = get_store()
    
    # Create or retrieve conversation
    conversation_id = request.conversation_id or str(uuid.uuid4())
    context = store.get_or_create(conversation_id, request.user_id)
    
    # Add user message to context
    context.add_message(MessageRole.USER, request.message)
    
    try:
        # TODO: Integrate with actual workflow
        # For now, return placeholder response
        
        # Build system context injection
        system_context = context.get_system_prompt_injection()
        
        # Call to workflow with enhanced context
        response_text = f"[Echo] You said: {request.message}"
        sources = []
        confidence = 0.8
        
        # Add assistant response to context
        context.add_message(
            MessageRole.ASSISTANT,
            response_text,
            sources=sources,
            confidence=confidence
        )
        
        # Save updated context
        store.save(context)
        
        return ChatMessageResponse(
            response=response_text,
            conversation_id=conversation_id,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            sources=sources,
            confidence=confidence,
            thinking_process=system_context if system_context else None,
            conversation_summary=context.get_conversation_summary() if len(context.messages) > 2 else None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/conversations/{conversation_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str, store = None):
    """
    Get full conversation history
    
    Args:
        conversation_id: ID of conversation to retrieve
    
    Returns:
        ConversationHistoryResponse with all messages and metadata
    """
    if store is None:
        store = get_store()
    
    context = store.get_or_create(conversation_id)
    
    return ConversationHistoryResponse(
        conversation_id=context.conversation_id,
        messages=[m.to_dict() for m in context.messages],
        metadata={
            "intent": context.detected_intent,
            "topics": context.detected_topics,
            "user_profile": context.user_profile,
            "message_count": len(context.messages)
        },
        created_at=context.created_at,
        last_updated=context.last_updated
    )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, store = None):
    """
    Delete a conversation and its history
    
    Args:
        conversation_id: ID of conversation to delete
    """
    if store is None:
        store = get_store()
    
    try:
        store.delete(conversation_id)
        return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/{conversation_id}/clear")
async def clear_conversation(conversation_id: str, store = None):
    """
    Clear conversation history but keep metadata
    
    Args:
        conversation_id: ID of conversation to clear
    """
    if store is None:
        store = get_store()
    
    try:
        context = store.get_or_create(conversation_id)
        context.messages.clear()
        store.save(context)
        return {"status": "success", "message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/conversations")
async def get_user_conversations(user_id: str, store = None):
    """
    Get all conversations for a user
    
    Args:
        user_id: User ID to retrieve conversations for
    
    Returns:
        List of conversations with metadata
    """
    if store is None:
        store = get_store()
    
    try:
        conversations = store.get_user_conversations(user_id)
        return {
            "user_id": user_id,
            "conversations": [
                {
                    "id": c.conversation_id,
                    "created_at": c.created_at.isoformat(),
                    "last_updated": c.last_updated.isoformat(),
                    "message_count": len(c.messages),
                    "intent": c.detected_intent,
                    "topics": c.detected_topics
                }
                for c in conversations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket support for real-time conversation
@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str, store = None):
    """
    WebSocket endpoint for real-time chat with persistent context
    
    Allows streaming responses and maintains conversation state
    across multiple connected clients.
    """
    if store is None:
        store = get_store()
    
    await websocket.accept()
    
    try:
        context = store.get_or_create(conversation_id)
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            user_id = data.get("user_id")
            
            if not message:
                continue
            
            # Add to context
            context.user_id = user_id or context.user_id
            context.add_message(MessageRole.USER, message)
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "user_message",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # TODO: Stream response from workflow
            response = f"Received: {message}"
            
            # Add response to context
            context.add_message(MessageRole.ASSISTANT, response)
            store.save(context)
            
            # Send response
            await websocket.send_json({
                "type": "assistant_message",
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "conversation_summary": context.get_conversation_summary()
            })
    
    except WebSocketDisconnect:
        store.save(context)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
