"""Tests for the services layer."""

import pytest
from datetime import datetime
import uuid
from unittest.mock import patch, mock_open

from src import app_services
from src.models import api_models
from src.models.database_models import MessageType
from src.services.mysql_service import *

# Test database configuration
TEST_DB_URL = "mysql+aiomysql://root:root@localhost:3306/mcp_test"

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
    # Mock LLM response
    mock_llm_response = "New mock LLM draft."
    mocker.patch("src.llm_client.get_llm_completion", return_value=mock_llm_response)
    
    # Add initial data
    thread_name = "test_thread"
    user_id = "test_user"
    
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
    assert drafts[0].msg_content == mock_llm_response

@pytest.mark.asyncio
async def test_create_revised_draft_from_feedback(mocker):
    """
    Tests that a new draft is created and the agent context is stored,
    while the old draft is deleted.
    """
    # Mock LLM response
    mock_llm_response = "Mock LLM revised draft."
    mocker.patch("src.llm_client.get_llm_completion", return_value=mock_llm_response)
    
    # Add initial data
    thread_name = "test_thread"
    user_id = "test_user"
    timestamp = datetime.now()
    
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
    agent_id = str(uuid.uuid4())
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
        thread_name=thread_name,
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
    assert drafts[0].msg_content == mock_llm_response
    assert drafts[0].agent_id == agent_id
    
    # Agent context should be stored
    agent = await get_agent(user_id, agent_id)
    assert agent is not None 