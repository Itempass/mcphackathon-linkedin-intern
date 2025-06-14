from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, DateTime, Text, Enum as SQLEnum
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

class AgentMessageType(enum.Enum):
    system_prompt = "system_prompt"
    user_prompt = "user_prompt"
    toolcall = "toolcall"
    toolcall_response = "toolcall_response"
    toolcall_response_error = "toolcall_response_error"
    toolcall_response_success = "toolcall_response_success"
    toolcall_response_warning = "toolcall_response_warning"
    toolcall_response_info = "toolcall_response_info"

# 3. Define the Message model
class Message(Base):
    __tablename__ = "messages"

    # id: hash of sender_date, timestamp, content
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # user_id: hash of user name
    user_id: Mapped[str] = mapped_column(String(255))
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

    # Relationship to Agent
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="messages")

# 4. Define the Agent model
class Agent(Base):
    __tablename__ = "agents"

    # id: UUID
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationship to Messages (the messages field from UML is represented as a relationship)
    messages: Mapped[list["Message"]] = relationship(back_populates="agent")

# 5. Define the AgentThread model
class AgentThread(Base):
    __tablename__ = "agent_threads"

    id: Mapped[int] = mapped_column(primary_key=True)
    # type: AgentMessageType
    type: Mapped[AgentMessageType] = mapped_column(SQLEnum(AgentMessageType))
    # content: String
    content: Mapped[str] = mapped_column(Text)
    # Optional: link to agent for better organization
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"), nullable=True)
    
    # Relationship to Agent
    agent: Mapped[Optional["Agent"]] = relationship() 