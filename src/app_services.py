"""
Services layer for handling business logic and database operations.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.models import api_models
from src.models.database_models import MessageType
from src.services.mysql_service import *
from src.llm_client import get_llm_completion

async def process_thread_and_create_draft(request: api_models.APISendMessageRequest) -> str:
    """
    Service to handle processing a thread of messages, storing new ones,
    invalidating old drafts, and creating a new draft using the LLM.
    This logic is based on the loading_messages_sequence_diagram.
    """
    print(f"SERVICE: Processing thread {request.thread_name} for user {request.user_id}")

    # 1. Get existing messages from database
    existing_messages = await get_all_messages_of_thread(request.user_id, request.thread_name)
    existing_message_ids = {msg.id for msg in existing_messages}
    new_api_messages = [msg for msg in request.messages if msg.message_id not in existing_message_ids]

    if not new_api_messages:
        print("SERVICE: No new messages found. No action taken.")
        return 

    print(f"SERVICE: Found {len(new_api_messages)} new messages.")

    # 2. Delete any existing drafts for this thread
    existing_drafts = [msg for msg in existing_messages if msg.type == MessageType.DRAFT]
    for draft in existing_drafts:
        print(f"SERVICE: Deleting existing draft {draft.id} for thread {request.thread_name}.")
        await remove_message(request.user_id, draft.id)

    # 3. Store the new messages
    for msg in new_api_messages:
        timestamp = datetime.strptime(f"{msg.date} {msg.time}", "%Y-%m-%d %H:%M:%S")
        message_id = create_message_id(msg.sender_name, timestamp, msg.message_content)
        
        await add_message(
            user_id=request.user_id,
            message_id=message_id,
            message_type=MessageType.MESSAGE,
            msg_content=msg.message_content,
            thread_name=request.thread_name,
            sender_name=msg.sender_name,
            timestamp=timestamp
        )
    print("SERVICE: New messages stored.")

    # 4. Get updated thread history and generate new draft
    thread_messages = await get_all_messages_of_thread(request.user_id, request.thread_name)
    thread_messages.sort(key=lambda msg: msg.timestamp)

    # Format messages for LLM
    llm_messages = [
        {"role": "system", "content": "Process thread prompt"},  # TODO: Load from file
        *[{
            "role": "user" if msg.sender_name != "Agent" else "assistant",
            "content": msg.msg_content
        } for msg in thread_messages if msg.type == MessageType.MESSAGE]
    ]

    # Generate draft with LLM
    draft_content = await get_llm_completion(llm_messages)
    draft_timestamp = datetime.now()
    draft_id = create_message_id("Agent", draft_timestamp, draft_content)

    # Store the draft
    await add_message(
        user_id=request.user_id,
        message_id=draft_id,
        message_type=MessageType.DRAFT,
        msg_content=draft_content,
        thread_name=request.thread_name,
        sender_name="Agent",
        timestamp=draft_timestamp
    )

    print(f"SERVICE: Created new draft {draft_id} for thread {request.thread_name}.")
    return draft_id

async def get_all_drafts_for_user(user_id: str) -> List[Any]:
    """
    Service to retrieve all messages of type=DRAFT for a given user.
    """
    print(f"SERVICE: Fetching drafts for user {user_id}")
    return await get_all_messages_of_type(user_id, MessageType.DRAFT)

async def delete_draft(request: api_models.APIRejectDraftRequest):
    """
    Service to delete a message of type=DRAFT from the database.
    """
    print(f"SERVICE: Attempting to delete draft {request.draft_message_id} for user {request.user_id}")
    success = await remove_message(request.user_id, request.draft_message_id)
    
    if success:
        print(f"SERVICE: Draft {request.draft_message_id} deleted.")
    else:
        print(f"SERVICE: Draft {request.draft_message_id} not found for user {request.user_id}.")

async def create_revised_draft_from_feedback(request: api_models.APIProcessFeedbackRequest) -> str:
    """
    Service to create a revised draft based on feedback.
    This logic is based on the reject_draft_sequence_diagram.
    """
    print(f"SERVICE: Processing feedback for draft {request.draft_message_id}")

    # Get the old draft and its thread
    thread_messages = await get_all_messages_of_thread(request.user_id, request.thread_name)
    old_draft = next((msg for msg in thread_messages if msg.id == request.draft_message_id), None)
    if not old_draft:
        raise ValueError(f"Draft {request.draft_message_id} not found")

    # Get or create agent context
    agent_id = old_draft.agent_id or str(uuid.uuid4())
    agent = await get_agent(request.user_id, agent_id)
    
    # Format messages for LLM
    llm_messages = [
        {"role": "system", "content": "Revise draft prompt"},  # TODO: Load from file
        *[{
            "role": "user" if msg.sender_name != "Agent" else "assistant",
            "content": msg.msg_content
        } for msg in thread_messages if msg.type == MessageType.MESSAGE],
        {"role": "assistant", "content": old_draft.msg_content},
        {"role": "user", "content": f"FEEDBACK: {request.feedback}"}
    ]

    # Generate revised draft with LLM
    revised_content = await get_llm_completion(llm_messages)
    draft_timestamp = datetime.now()
    draft_id = create_message_id("Agent", draft_timestamp, revised_content)

    # Delete old draft
    await remove_message(request.user_id, request.draft_message_id)

    # Store new draft
    await add_message(
        user_id=request.user_id,
        message_id=draft_id,
        message_type=MessageType.DRAFT,
        msg_content=revised_content,
        thread_name=request.thread_name,
        sender_name="Agent",
        timestamp=draft_timestamp,
        agent_id=agent_id
    )

    # Store agent context
    await upsert_agent(request.user_id, agent_id, llm_messages)

    print(f"SERVICE: Created revised draft {draft_id} with agent {agent_id}")
    return draft_id 