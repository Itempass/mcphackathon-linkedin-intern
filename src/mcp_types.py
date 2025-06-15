"""Shared types for the MCP system."""

import enum
from typing import Optional, Dict, Any
from src.models.database_models import MessageType

class ToolCallType(enum.Enum):
    """Tool call types as shown in the sequence diagrams."""
    SUGGEST_DRAFT = "suggest_draft"
    FIND_SIMILAR_MESSAGES = "find_similar_messages"
    SEMANTIC_SEARCH = "semantic_search"
    END_WORK = "end_work"

class MCPMessage:
    """Represents a message in the MCP system."""
    def __init__(
        self,
        content: str,
        msg_type: MessageType,
        thread_name: str,
        sender_name: str,
        user_id: str,
        agent_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.content = content
        self.msg_type = msg_type
        self.thread_name = thread_name
        self.sender_name = sender_name
        self.user_id = user_id
        self.agent_id = agent_id
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "msg_content": self.content,
            "type": self.msg_type.value,
            "thread_name": self.thread_name,
            "sender_name": self.sender_name,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create message from dictionary data."""
        return cls(
            content=data["msg_content"],
            msg_type=MessageType(data["type"]),
            thread_name=data["thread_name"],
            sender_name=data["sender_name"],
            user_id=data["user_id"],
            agent_id=data.get("agent_id"),
            timestamp=data.get("timestamp")
        )

class ToolCall:
    """Represents a tool call from the agent."""
    def __init__(self, tool_type: ToolCallType, **kwargs):
        self.tool_type = tool_type
        self.kwargs = kwargs 