import uuid
from typing import List, Dict
from .models import api_models, internal_models
from .models.internal_models import InternalMessage, MessageType
from . import llm_client

# Helper to load prompts from files
def _load_prompt(file_name: str) -> str:
    with open(f"src/prompts/{file_name}", "r") as f:
        return f.read().strip()

# A mock database for storing ALL messages, aligned with the new unified model.
# In Phase 5, this will be replaced with a real database connection.
MOCK_MESSAGES_DB: List[InternalMessage] = [
    InternalMessage(
        id="draft-123",
        user_id="test_user",
        thread_name="example-thread-1",
        sender_name="Agent",
        msg_content="This is a draft message from the service.",
        type=MessageType.DRAFT
    ),
    InternalMessage(
        id="msg-abc",
        user_id="test_user",
        thread_name="example-thread-1",
        sender_name="Human",
        msg_content="This is a regular message.",
        type=MessageType.MESSAGE
    ),
    InternalMessage(
        id="draft-456",
        user_id="test_user",
        thread_name="example-thread-2",
        sender_name="Agent",
        msg_content="This is another draft message from the service.",
        type=MessageType.DRAFT
    ),
]

# A mock database for storing agent context. Maps agent_id to the list of messages sent to the LLM.
MOCK_AGENTS_DB: Dict[str, List[Dict[str, str]]] = {}

def process_thread_and_create_draft(request: api_models.APISendMessageRequest) -> str:
    """
    Service to handle processing a thread of messages, storing new ones,
    invalidating old drafts, and creating a new draft using the LLM.
    This logic is based on the loading_messages_sequence_diagram.
    """
    print(f"SERVICE: Processing thread {request.thread_name} for user {request.user_id}")

    # 1. Find new messages by comparing request with mock DB
    existing_message_ids = {
        msg.id for msg in MOCK_MESSAGES_DB
        if msg.thread_name == request.thread_name and msg.type == MessageType.MESSAGE
    }
    new_api_messages = [msg for msg in request.messages if msg.message_id not in existing_message_ids]

    if not new_api_messages:
        print("SERVICE: No new messages found. No action taken.")
        return 

    print(f"SERVICE: Found {len(new_api_messages)} new messages.")

    # 2. Invalidate and delete any existing draft for this thread
    draft_to_delete = next((
        msg for msg in MOCK_MESSAGES_DB
        if msg.thread_name == request.thread_name and msg.type == MessageType.DRAFT
    ), None)

    if draft_to_delete:
        print(f"SERVICE: Deleting existing draft {draft_to_delete.id} for thread {request.thread_name}.")
        MOCK_MESSAGES_DB.remove(draft_to_delete)

    # 3. Store the new messages
    for msg in new_api_messages:
        MOCK_MESSAGES_DB.append(
            InternalMessage(
                id=msg.message_id, # Use the message_id from the request
                user_id=request.user_id,
                thread_name=request.thread_name,
                sender_name=msg.sender_name,
                msg_content=msg.message_content,
                type=MessageType.MESSAGE
            )
        )
    print("SERVICE: New messages stored.")

    # 4. Generate a new draft using the full, updated conversation history
    full_thread_history = sorted(
        [msg for msg in MOCK_MESSAGES_DB
         if msg.thread_name == request.thread_name],
        key=lambda msg: msg.timestamp
    )
    
    
    system_prompt = _load_prompt("process_thread_prompt.txt")
    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in full_thread_history:
        llm_messages.append({"role": "user" if msg.sender_name != "Agent" else "assistant", "content": msg.msg_content})
    
    draft_content = llm_client.get_llm_completion(llm_messages)
    
    new_draft = InternalMessage(
        user_id=request.user_id,
        thread_name=request.thread_name,
        sender_name="Agent",
        msg_content=draft_content,
        type=MessageType.DRAFT
    )
    MOCK_MESSAGES_DB.append(new_draft)
    
    print(f"SERVICE: New draft {new_draft.id} created and stored.")
    return new_draft.id


def create_revised_draft_from_feedback(request: api_models.APIProcessFeedbackRequest):
    """
    Service to handle processing feedback and revising a draft.
    This deletes the old draft and creates a new one, saving the agent context.
    """
    print(f"SERVICE: Revising draft {request.draft_message_id} for user {request.user_id}")
    original_draft = next((msg for msg in MOCK_MESSAGES_DB if msg.id == request.draft_message_id and msg.user_id == request.user_id), None)

    if not original_draft:
        print(f"SERVICE: Draft {request.draft_message_id} not found for user {request.user_id}.")
        return

    # Get the agent_id from the original draft as per sequence diagram
    agent_id = original_draft.agent_id
    if not agent_id:
        print(f"SERVICE: No agent_id found for draft {request.draft_message_id}.")
        return

    # Get the agent context from the DB
    agent_context = MOCK_AGENTS_DB.get(agent_id)
    if not agent_context:
        print(f"SERVICE: Agent context not found for agent_id {agent_id}.")
        return

    # Retrieve the full conversation context from the mock DB, including the draft
    thread_context = [
        msg for msg in MOCK_MESSAGES_DB
        if msg.thread_name == original_draft.thread_name
    ]
    # Ensure messages are in chronological order
    thread_context.sort(key=lambda x: x.timestamp)

    # Format messages for the LLM, starting with the existing agent context
    llm_messages = agent_context.copy()  # Use existing context
    
    # Add the user's new feedback as the final message
    llm_messages.append({"role": "user", "content": f"Here is my feedback on the draft: {request.feedback}"})
    
    revised_content = llm_client.get_llm_completion(llm_messages)
    
    # Delete the old draft
    MOCK_MESSAGES_DB.remove(original_draft)
    print(f"SERVICE: Deleted old draft {original_draft.id}.")

    # Create and store the new draft, using the same agent_id
    new_draft = InternalMessage(
        user_id=request.user_id,
        thread_name=original_draft.thread_name,
        sender_name="Agent",
        msg_content=revised_content,
        type=MessageType.DRAFT,
        agent_id=agent_id  # Reuse the same agent_id
    )
    MOCK_MESSAGES_DB.append(new_draft)
    print(f"SERVICE: Created new draft {new_draft.id} with existing agent context.")

    # Update the agent context in the DB with the new messages
    MOCK_AGENTS_DB[agent_id] = llm_messages
    print(f"SERVICE: Updated agent context for agent_id {agent_id}.")


def get_all_drafts_for_user(user_id: str) -> List[InternalMessage]:
    """
    Service to retrieve all messages of type=DRAFT for a given user.
    """
    print(f"SERVICE: Fetching drafts for user {user_id}")
    user_drafts = [
        msg for msg in MOCK_MESSAGES_DB 
        if msg.user_id == user_id and msg.type == MessageType.DRAFT
    ]
    return user_drafts


def delete_draft(request: api_models.APIRejectDraftRequest):
    """
    Service to delete a message of type=DRAFT from the mock database.
    """
    print(f"SERVICE: Attempting to delete draft {request.draft_message_id} for user {request.user_id}")
    
    initial_count = len(MOCK_MESSAGES_DB)
    MOCK_MESSAGES_DB[:] = [
        msg for msg in MOCK_MESSAGES_DB 
        if not (msg.id == request.draft_message_id and msg.user_id == request.user_id)
    ]
    
    if len(MOCK_MESSAGES_DB) < initial_count:
        print(f"SERVICE: Mock draft {request.draft_message_id} deleted.")
    else:
        print(f"SERVICE: Mock draft {request.draft_message_id} not found for user {request.user_id}.") 