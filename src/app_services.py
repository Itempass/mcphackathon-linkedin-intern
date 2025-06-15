"""
Services layer for handling business logic and database operations.
"""

import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import traceback

from src.models import api_models
from src.models.database_models import MessageType
from src.models.internal_models import InternalMessage
from src.services.mysql_service import *
from src.agent import run_intelligent_agent
from fastmcp import Client

async def process_thread_and_create_draft(request: api_models.APISendMessageRequest, mcp_clients: List[Client]) -> Optional[str]:
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
        return None

    print(f"SERVICE: Found {len(new_api_messages)} new messages.")

    # 2. Delete any existing drafts for this thread
    existing_drafts = [msg for msg in existing_messages if msg.type == MessageType.DRAFT]
    for draft in existing_drafts:
        print(f"SERVICE: Deleting existing draft {draft.id} for thread {request.thread_name}.")
        await remove_message(request.user_id, draft.id)

    # 3. Store the new messages
    for msg in new_api_messages:
        timestamp = datetime.strptime(f"{msg.date} {msg.time}", "%Y-%m-%d %H:%M:%S")
        message_id = msg.message_id
        
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
    try:
        thread_messages = await get_all_messages_of_thread(request.user_id, request.thread_name)
        thread_messages.sort(key=lambda msg: msg.timestamp)

        # Run the agent to process the thread and suggest a draft
        agent_id = str(uuid.uuid4())
        
        # Construct a rich, conversational prompt for the agent
        history_str = "\n".join([f"- {msg.sender_name}: {msg.msg_content}" for msg in thread_messages if msg.type == MessageType.MESSAGE])
        system_prompt = open("src/prompts/process_thread_prompt.txt").read()
        messages = [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""A new message has arrived in my message thread with '{request.thread_name}'. Please generate a helpful draft reply.

Here is the conversation history so far:
---
{history_str}
---

Analyze the conversation and suggest a suitable draft."""
            }
        ]
        print("SERVICE: agent about to start.")
        conversation_history = await run_intelligent_agent(
            mcp_clients=mcp_clients,
            user_id=request.user_id,
            agent_id=agent_id,
            messages=messages
        )

        # Extract draft from the agent's final action by checking for a specific tool call
        draft_content = None
        if conversation_history:
            # Check the last message from the assistant for a 'suggest_draft' tool call
            last_message = conversation_history[-1]
            if last_message.get("role") == "assistant" and last_message.get("tool_calls"):
                for tool_call in last_message["tool_calls"]:
                    if tool_call.get("function", {}).get("name") == "suggest_draft":
                        try:
                            args = json.loads(tool_call["function"]["arguments"])
                            draft_content = args.get("draft_content")
                            break 
                        except (json.JSONDecodeError, AttributeError):
                            print("SERVICE: Could not parse draft from tool call arguments.")

        # Save the agent information with conversation history, regardless of draft creation
        print(f"SERVICE: Attempting to save agent {agent_id} with conversation history.")
        await upsert_agent(request.user_id, agent_id, messages_array=conversation_history)
        print(f"SERVICE: Successfully saved agent {agent_id}.")

        # Only store a draft if one was successfully created by the agent
        if draft_content:
            all_current_thread_messages = await get_all_messages_of_thread(request.user_id, request.thread_name)
            
            # Extract message IDs from thread_messages that were used to create the agent context
            thread_message_ids = {msg.id for msg in thread_messages if msg.type == MessageType.MESSAGE}
            
            # Check for new messages that weren't in the agent's context
            new_messages = [msg for msg in all_current_thread_messages 
                        if msg.type == MessageType.MESSAGE and 
                        msg.id not in thread_message_ids]

            if new_messages:
                print("SERVICE: There are newer messages than the agent's context when making this draft. Draft discarded.")
                return None
            # if there is already a draft for the exaxt same thread, discard the draft
            if len(new_messages) == 0 and any(msg.type == MessageType.DRAFT for msg in all_current_thread_messages):
                print("SERVICE: A draft already exists for this exact same thread. Draft discarded.")
                return None
            
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
                timestamp=draft_timestamp,
                agent_id=agent_id
            )

            print(f"SERVICE: Created new draft {draft_id} for thread {request.thread_name}.")
            return draft_id
        
        print("SERVICE: Agent did not produce a draft. No new draft created.")
        return None
    except Exception as e:
        print(f"SERVICE: An unexpected error occurred in process_thread_and_create_draft: {e}")
        print(traceback.format_exc())
        return None

async def get_all_drafts_for_user(user_id: str) -> List[InternalMessage]:
    """
    Service to retrieve all messages of type=DRAFT for a given user.
    """
    print(f"SERVICE: Fetching drafts for user {user_id}")
    db_drafts = await get_all_messages_of_type(user_id, MessageType.DRAFT)
    
    # Convert database models to internal Pydantic models
    internal_drafts = [
        InternalMessage(
            id=draft.id,
            user_id=draft.user_id,
            thread_name=draft.thread_name,
            sender_name=draft.sender_name,
            msg_content=draft.msg_content,
            type=draft.type,
            timestamp=draft.timestamp,
            agent_id=uuid.UUID(draft.agent_id) if draft.agent_id else None
        ) for draft in db_drafts
    ]
    
    return internal_drafts

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

async def create_revised_draft_from_feedback(request: api_models.APIProcessFeedbackRequest, mcp_clients: List[Client]) -> Optional[str]:
    """
    Service to create a revised draft based on feedback.
    This logic is based on the reject_draft_sequence_diagram.
    """
    print(f"SERVICE: Processing feedback for draft {request.draft_message_id}")

    # 1. Get the draft that needs revision
    old_draft = await get_message(request.user_id, request.draft_message_id)
    if not old_draft:
        raise ValueError(f"Draft {request.draft_message_id} not found")
    
    # Get the thread name from the draft message
    thread_name = old_draft.thread_name
    
    # Get all thread messages
    thread_messages = await get_all_messages_of_thread(request.user_id, thread_name)

    # 2. Set up the agent to generate a revised draft
    agent_id = old_draft.agent_id or str(uuid.uuid4())

    # Construct a conversational history for the agent
    messages = [
        {"role": "system", "content": "You are an expert assistant. Your goal is to revise a draft based on user feedback. Use the `suggest_draft` tool to provide the new version."},
        # Add original thread messages
        *[{
            "role": "user" if msg.sender_name != "Agent" else "assistant",
            "content": msg.msg_content
        } for msg in thread_messages if msg.type == MessageType.MESSAGE],
        # Add the assistant's previous attempt
        {"role": "assistant", "content": old_draft.msg_content},
        # Add the user's feedback
        {"role": "user", "content": f"Please revise your previous draft based on the following feedback: '{request.feedback}'. Provide a new draft using the `suggest_draft` tool."}
    ]
    
    conversation_history = await run_intelligent_agent(
        mcp_clients=mcp_clients,
        user_id=request.user_id,
        agent_id=agent_id,
        messages=messages
    )

    # 3. Extract the new draft from the agent's result by checking tool calls
    revised_content = None
    if conversation_history:
        last_message = conversation_history[-1]
        if last_message.get("role") == "assistant" and last_message.get("tool_calls"):
            for tool_call in last_message["tool_calls"]:
                if tool_call.get("function", {}).get("name") == "suggest_draft":
                    try:
                        args = json.loads(tool_call["function"]["arguments"])
                        revised_content = args.get("draft_content")
                        break
                    except (json.JSONDecodeError, AttributeError):
                        print("SERVICE: Could not parse revised draft from tool call arguments.")

    # 4. Delete the old draft and store the new one, if it exists
    if revised_content:
        draft_timestamp = datetime.now()
        draft_id = create_message_id("Agent", draft_timestamp, revised_content)
        await remove_message(request.user_id, request.draft_message_id)
        
        # Save the agent information with conversation history before adding the message
        await upsert_agent(request.user_id, agent_id, messages_array=conversation_history)
        
        await add_message(
            user_id=request.user_id,
            message_id=draft_id,
            message_type=MessageType.DRAFT,
            msg_content=revised_content,
            thread_name=thread_name,
            sender_name="Agent",
            timestamp=draft_timestamp,
            agent_id=agent_id
        )
        
        print(f"SERVICE: Created revised draft {draft_id} with agent {agent_id}")
        return draft_id

    print(f"SERVICE: Agent did not produce a revised draft for {request.draft_message_id}.")
    return None 