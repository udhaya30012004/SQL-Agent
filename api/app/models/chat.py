"""
Chat ORM Models

Defines the database tables for conversational sessions and messages.
Sessions are scoped to authenticated users via a foreign key to the ``users`` table.
"""

import datetime
import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.app.db.session import Base


class ChatSession(Base):
    """
    Represents a conversational session.
    The ID maps directly to the LangGraph thread_id.
    Each session belongs to exactly one authenticated user.
    """
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_type = Column(String, nullable=False)  # "sql" or "pandas"
    title = Column(String, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    # Relationships
    owner = relationship("User", back_populates="sessions")
    messages = relationship(
        "ChatMessage", 
        back_populates="session", 
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at"
    )


class ChatMessage(Base):
    """
    Represents a single message in a conversation.
    Stores user inputs and assistant response metadata.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    # Agent output metadata
    sql_query = Column(Text, nullable=True)     # For SQL Agent
    chart_path = Column(String, nullable=True)  # For SQL Agent charts URL/path
    _chart_spec = Column("chart_spec", Text, nullable=True) # Serialized JSON chart spec
    error = Column(Text, nullable=True)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    @property
    def chart_spec(self):
        """Getter for chart specification JSON."""
        if self._chart_spec:
            try:
                return json.loads(self._chart_spec)
            except Exception:
                return {}
        return {}

    @chart_spec.setter
    def chart_spec(self, value):
        """Setter for chart specification JSON."""
        if value:
            self._chart_spec = json.dumps(value)
        else:
            self._chart_spec = None
