# This file will hold internal data models, such as SQLAlchemy ORM classes. 

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import enum
import uuid
from src.models.database_models import MessageType

# Add ToolCallType and ToolCall to support tests
class ToolCallType(enum.Enum):
    SUGGEST_DRAFT = "suggest_draft"
    FIND_SIMILAR_MESSAGES = "find_similar_messages"
    SEMANTIC_SEARCH = "semantic_search"
    END_WORK = "end_work"

class ToolCall(BaseModel):
    tool_type: ToolCallType
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, tool_type: ToolCallType, **kwargs):
        super().__init__(tool_type=tool_type, kwargs=kwargs)

# Add MCPMessage to support MCP client tests
class MCPMessage(BaseModel):
    content: str
    msg_type: MessageType
    thread_name: str
    sender_name: str
    user_id: str
    agent_id: Optional[str] = None

class InternalMessage(BaseModel):
    """
    Represents a message in the system, aligned with the database schema.
    A message can be a draft or a final message.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    thread_name: str
    sender_name: str
    msg_content: str
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: Optional[uuid.UUID] = None

    # This is a helper for converting to the API model if needed.
    def to_api_draft_message(self) -> "APIDraftMessage":
        from .api_models import APIDraftMessage
        return APIDraftMessage(
            thread_name=self.thread_name,
            draft_message_id=self.id,
            draft_message_content=self.msg_content
        ) 