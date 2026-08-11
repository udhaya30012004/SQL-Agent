"""
Connector ORM models.

The MVP stores pairing/status metadata in the backend database while the live
WebSocket connection and pending jobs are kept in memory by connector_manager.
"""

import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from api.app.db.session import Base


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False, default="Local Connector")
    pairing_code = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    last_seen_at = Column(DateTime, nullable=True)

    connections = relationship(
        "ConnectorConnection",
        back_populates="connector",
        cascade="all, delete-orphan",
    )


class ConnectorConnection(Base):
    __tablename__ = "connector_connections"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    connector_id = Column(
        String,
        ForeignKey("connectors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False, default="PostgreSQL Connection")
    db_type = Column(String, nullable=False, default="postgresql")
    connection_string = Column(Text, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    connector = relationship("Connector", back_populates="connections")
