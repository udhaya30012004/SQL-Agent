"""
Chat Pydantic Schemas

Request / response models for the chatbot endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ==========================================
# CHAT MESSAGE SCHEMAS
# ==========================================

class ChatMessageBase(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: str
    sql_query: Optional[str] = None
    chart_path: Optional[str] = None
    chart_spec: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: str
    created_at: datetime
    
    # Rich details populated for assistant replies
    sql_query: Optional[str] = None
    chart_path: Optional[str] = None
    chart_spec: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# CHAT SESSION SCHEMAS
# ==========================================

class ChatSessionBase(BaseModel):
    id: str
    user_id: str
    agent_type: str  # "sql" or "pandas"
    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# API ENDPOINT REQUESTS
# ==========================================

class ChatRequest(BaseModel):
    """
    Standard request payload to send a query to the chatbot.
    """
    session_id: str  # References the ChatSession ID
    question: str    # User's natural language question
    response_mode: str = "both"  # "answer", "chart", or "both"
    
    # Optional SQL Agent parameter
    connection_string: Optional[str] = None


class SessionCreateRequest(BaseModel):
    """
    Payload required to register/initialize a new ChatSession.
    user_id is automatically populated from the JWT token.
    """
    agent_type: str  # "sql" or "pandas"
    title: Optional[str] = None
