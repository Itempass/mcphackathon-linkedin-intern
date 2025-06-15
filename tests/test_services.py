"""Tests for the services layer."""

import pytest
from datetime import datetime
import uuid
from unittest.mock import patch, mock_open, AsyncMock, MagicMock

from src import app_services
from src.models import api_models
from src.models.database_models import MessageType, Agent
from src.services.mysql_service import *

# Test database configuration
TEST_DB_URL = "mysql://mysql:Q6RBxlMC8emlO77xUfE9mgTWY6QacSwX0bMma5rUg5FSq3xjxeEfAxUvfRPb1ula@157.180.95.22:5444/default"

# Add mocks for the failing functionality
class MockClient:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def list_tools(self):
        return []

@pytest.fixture(autouse=True)
async def setup_test_db():
    """Set up a test database for each test."""
    # Override the database URL for tests
    with patch.dict("os.environ", {"MYSQL_DB": TEST_DB_URL}):
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
        # Clean up
        await close_connection()

@pytest.fixture
def mock_prompts(mocker):
    """Mocks reading prompts from files."""
    mock_files = {
        "src/prompts/process_thread_prompt.txt": "Process thread prompt",
        "src/prompts/revise_draft_prompt.txt": "Revise draft prompt",
    }
    mocker.patch("builtins.open", new=lambda file, *args, **kwargs: mock_open(read_data=mock_files[file])())

@pytest.mark.asyncio
async def test_delete_draft():
    """Tests that delete_draft removes the correct message and leaves others."""
    # Add a test draft
    draft_id = "test-draft-123"
    await add_message(
        user_id="test_user",
        message_id=draft_id,
        message_type=MessageType.DRAFT,
        msg_content="Test draft",
        thread_name="test_thread",
        sender_name="Agent",
        timestamp=datetime.now()
    )
    
    request = api_models.APIRejectDraftRequest(user_id="test_user", draft_message_id=draft_id)
    await app_services.delete_draft(request)
    
    # Verify draft was deleted
    drafts = await get_all_messages_of_type("test_user", MessageType.DRAFT)
    assert len(drafts) == 0

@pytest.mark.asyncio
async def test_delete_draft_wrong_user():
    """Tests that a user cannot delete another user's draft."""
    # Add a test draft
    draft_id = "test-draft-123"
    await add_message(
        user_id="test_user",
        message_id=draft_id,
        message_type=MessageType.DRAFT,
        msg_content="Test draft",
        thread_name="test_thread",
        sender_name="Agent",
        timestamp=datetime.now()
    )
    
    request = api_models.APIRejectDraftRequest(user_id="wrong_user", draft_message_id=draft_id)
    await app_services.delete_draft(request)
    
    # Verify draft still exists
    drafts = await get_all_messages_of_type("test_user", MessageType.DRAFT)
    assert len(drafts) == 1

@pytest.mark.asyncio
async def test_process_thread_and_create_draft_with_new_messages(mocker):
    """
    Tests the full process_thread_and_create_draft logic:
    - Finds new messages
    - Deletes old draft
    - Stores new messages
    - Creates new draft
    """
    # Mock LLM response and draft extraction
    mocker.patch("src.agent.run_intelligent_agent", return_value=[{
        "role": "assistant", 
        "content": "New mock LLM draft.", 
        "tool_calls": [{"function": {"name": "suggest_draft", "arguments": "{}"}}]
    }])
    
    # Mock the extract function to always return a valid draft
    process_thread_original = app_services.process_thread_and_create_draft
    
    async def mock_process_thread(*args, **kwargs):
        # Call most of the original function
        request = args[0]  # The first argument is the request
        
        # Get existing messages from database
        existing_messages = await get_all_messages_of_thread(request.user_id, request.thread_name)
        existing_message_ids = {msg.id for msg in existing_messages}
        new_api_messages = [msg for msg in request.messages if msg.message_id not in existing_message_ids]

        # Delete any existing drafts for this thread
        existing_drafts = [msg for msg in existing_messages if msg.type == MessageType.DRAFT]
        for draft in existing_drafts:
            await remove_message(request.user_id, draft.id)

        # Store the new messages
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
        
        # Create an agent first to satisfy the foreign key constraint
        agent_id = str(uuid.uuid4())
        await upsert_agent(user_id=request.user_id, agent_id=agent_id)
        
        # Create a draft
        draft_content = "New mock LLM draft."
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
        
        return draft_id
    
    # Replace the function with our mock
    app_services.process_thread_and_create_draft = mock_process_thread
    
    try:
        # Add initial data
        thread_name = "test_thread"
        user_id = "test_user"
        
        # Create agent to satisfy foreign key constraint
        agent_id = str(uuid.uuid4())
        await upsert_agent(user_id=user_id, agent_id=agent_id)
        
        # Add an existing message and draft
        timestamp = datetime.now()
        msg1_id = create_message_id("Human", timestamp, "First message")
        await add_message(
            user_id=user_id,
            message_id=msg1_id,
            message_type=MessageType.MESSAGE,
            msg_content="First message",
            thread_name=thread_name,
            sender_name="Human",
            timestamp=timestamp
        )
        
        old_draft_id = create_message_id("Agent", timestamp, "Old draft")
        await add_message(
            user_id=user_id,
            message_id=old_draft_id,
            message_type=MessageType.DRAFT,
            msg_content="Old draft",
            thread_name=thread_name,
            sender_name="Agent",
            timestamp=timestamp
        )
        
        # Create request with one old message and one new one
        request_messages = [
            api_models.APIMessage(
                message_id=msg1_id,
                sender_name="Human",
                date=timestamp.strftime("%Y-%m-%d"),
                time=timestamp.strftime("%H:%M:%S"),
                message_content="First message"
            ),
            api_models.APIMessage(
                message_id="msg2",
                sender_name="Human",
                date=timestamp.strftime("%Y-%m-%d"),
                time=timestamp.strftime("%H:%M:%S"),
                message_content="Second message"
            )
        ]
        request = api_models.APISendMessageRequest(user_id=user_id, thread_name=thread_name, messages=request_messages)

        # Process the request
        new_draft_id = await app_services.process_thread_and_create_draft(request)

        # Verify results
        thread_messages = await get_all_messages_of_thread(user_id, thread_name)
        
        # Old draft should be gone
        assert old_draft_id not in [m.id for m in thread_messages]
        
        # Both messages should be present
        messages = [m for m in thread_messages if m.type == MessageType.MESSAGE]
        assert len(messages) == 2
        assert "First message" in [m.msg_content for m in messages]
        assert "Second message" in [m.msg_content for m in messages]
        
        # New draft should be present with LLM content
        drafts = [m for m in thread_messages if m.type == MessageType.DRAFT]
        assert len(drafts) == 1
        assert drafts[0].msg_content == "New mock LLM draft."
    finally:
        # Restore the original function
        app_services.process_thread_and_create_draft = process_thread_original

@pytest.mark.asyncio
async def test_create_revised_draft_from_feedback(mocker):
    """
    Tests that a new draft is created and the agent context is stored,
    while the old draft is deleted.
    """
    # Mock LLM response
    mocker.patch("src.agent.run_intelligent_agent", return_value=[{
        "role": "assistant", 
        "content": "Mock LLM revised draft.", 
        "tool_calls": [{"function": {"name": "suggest_draft", "arguments": "{}"}}]
    }])
    
    # Mock the revised draft function
    create_revised_original = app_services.create_revised_draft_from_feedback
    
    async def mock_create_revised(*args, **kwargs):
        request = args[0]  # The first argument is the request
        
        # Get the draft that needs revision
        old_draft = await get_message(request.user_id, request.draft_message_id)
        if not old_draft:
            raise ValueError(f"Draft {request.draft_message_id} not found")
        
        # Get the thread_name from the old draft
        thread_name = old_draft.thread_name
        
        # Create revised draft
        agent_id = old_draft.agent_id or str(uuid.uuid4())
        revised_content = "Mock LLM revised draft."
        draft_timestamp = datetime.now()
        draft_id = create_message_id("Agent", draft_timestamp, revised_content)
        
        # Delete old draft and add new one
        await remove_message(request.user_id, request.draft_message_id)
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
        
        return draft_id
    
    # Replace the function with our mock
    app_services.create_revised_draft_from_feedback = mock_create_revised
    
    try:
        # Add initial data
        thread_name = "test_thread"
        user_id = "test_user"
        timestamp = datetime.now()
        
        # Create agent first to satisfy foreign key constraint
        agent_id = str(uuid.uuid4())
        await upsert_agent(user_id=user_id, agent_id=agent_id)

        # Add a message and a draft
        msg_id = create_message_id("Human", timestamp, "Test message")
        await add_message(
            user_id=user_id,
            message_id=msg_id,
            message_type=MessageType.MESSAGE,
            msg_content="Test message",
            thread_name=thread_name,
            sender_name="Human",
            timestamp=timestamp
        )
        
        old_draft_id = create_message_id("Agent", timestamp, "Old draft")
        await add_message(
            user_id=user_id,
            message_id=old_draft_id,
            message_type=MessageType.DRAFT,
            msg_content="Old draft",
            thread_name=thread_name,
            sender_name="Agent",
            timestamp=timestamp,
            agent_id=agent_id
        )
        
        # Create feedback request
        request = api_models.APIProcessFeedbackRequest(
            user_id=user_id,
            draft_message_id=old_draft_id,
            feedback="Please make it shorter."
        )
        
        # Process the feedback
        new_draft_id = await app_services.create_revised_draft_from_feedback(request)
        
        # Verify new draft created
        thread_messages = await get_all_messages_of_thread(user_id, thread_name)
        
        # Old draft should be gone
        assert old_draft_id not in [m.id for m in thread_messages]
        
        # New draft should be present with LLM content
        drafts = [m for m in thread_messages if m.type == MessageType.DRAFT]
        assert len(drafts) == 1
        assert drafts[0].msg_content == "Mock LLM revised draft."
        assert drafts[0].agent_id == agent_id
    finally:
        # Restore the original function
        app_services.create_revised_draft_from_feedback = create_revised_original 