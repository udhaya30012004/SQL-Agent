"""
User ORM Model

Represents an authenticated user of the Agentic Data Analyst platform.
Each user can own multiple ChatSession records.
"""

import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from api.app.db.session import Base


class User(Base):
    """Registered platform user."""

    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    # One user → many chat sessions
    sessions = relationship(
        "ChatSession",
        back_populates="owner",
        cascade="all, delete-orphan",
        order_by="ChatSession.created_at.desc()",
    )
