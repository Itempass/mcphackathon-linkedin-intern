from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, Text, Enum as SQLEnum, func
from datetime import datetime
from typing import Optional
import enum
import uuid

# 1. Define a Base class for all models to inherit from
class Base(DeclarativeBase):
    pass

# 2. Define enums
class MessageType(enum.Enum):
    DRAFT = "DRAFT"
    MESSAGE = "MESSAGE"

# 3. Define the Message model
class Message(Base):
    __tablename__ = "messages"

    # id: hash of sender_date, timestamp, content
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # user_id: hash of user name
    user_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # msg_content: String
    msg_content: Mapped[str] = mapped_column(Text)
    # type: MessageType
    type: Mapped[MessageType] = mapped_column(SQLEnum(MessageType))
    # thread_name: String
    thread_name: Mapped[str] = mapped_column(String(255))
    # sender_name: String
    sender_name: Mapped[str] = mapped_column(String(255))
    # timestamp: DateTime (optional)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # agent_id: UUID (optional)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"), nullable=True)
    # created_at: DateTime
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

# 4. Define the Agent model
class Agent(Base):
    __tablename__ = "agents"

    # id: UUID
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # user_id: hash of user name
    user_id: Mapped[str] = mapped_column(String(255))
    # messages: JSON array of LLM conversation messages
    messages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Store JSON as text 
    # created_at: DateTime
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) 