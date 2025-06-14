# This file will hold internal data models, such as SQLAlchemy ORM classes. 

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from src.models.database_models import MessageType

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