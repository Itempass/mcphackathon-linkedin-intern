from pydantic import BaseModel
from typing import List
from datetime import date, time

class APIMessage(BaseModel):
    message_id: str
    sender_name: str
    date: date
    time: time
    message_content: str

class APISendMessageRequest(BaseModel):
    user_id: str
    thread_name: str
    messages: List[APIMessage]

class APIProcessFeedbackRequest(BaseModel):
    user_id: str
    draft_message_id: str
    feedback: str

class APIRejectDraftRequest(BaseModel):
    user_id: str
    draft_message_id: str

class APIDraftMessage(BaseModel):
    thread_name: str
    draft_message_id: str
    draft_message_content: str

class APIDraftMessageResponse(BaseModel):
    draft_messages: List[APIDraftMessage] 