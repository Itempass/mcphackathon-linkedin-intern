import pytest
from src import services, models
from src.models.internal_models import MessageType
from unittest.mock import mock_open

PROMPT_PROCESS = "Process prompt"
PROMPT_REVISE = "Revise prompt"

@pytest.fixture(autouse=True)
def reset_mock_db():
    """
    This fixture runs before each test, resetting the mock DB to a known state.
    This prevents tests from interfering with each other.
    """
    services.MOCK_MESSAGES_DB = [
        models.internal_models.InternalMessage(
            id="draft-123", user_id="test_user", thread_name="t1", sender_name="Agent",
            msg_content="This is the original draft.", type=MessageType.DRAFT
        ),
        models.internal_models.InternalMessage(
            id="msg-abc", user_id="test_user", thread_name="t1", sender_name="Human",
            msg_content="This is the message history for the draft.", type=MessageType.MESSAGE
        ),
        models.internal_models.InternalMessage(
            id="draft-456", user_id="test_user", thread_name="t2", sender_name="Agent",
            msg_content="This is another draft for test_user", type=MessageType.DRAFT
        ),
        models.internal_models.InternalMessage(
            id="draft-789", user_id="another_user", thread_name="t3", sender_name="Agent",
            msg_content="This is a draft for another_user", type=MessageType.DRAFT
        ),
    ]

@pytest.fixture
def mock_prompts(mocker):
    """Mocks reading prompts from files."""
    mock_files = {
        "src/prompts/process_thread_prompt.txt": PROMPT_PROCESS,
        "src/prompts/revise_draft_prompt.txt": PROMPT_REVISE,
    }
    mocker.patch("builtins.open", new=lambda file, *args, **kwargs: mock_open(read_data=mock_files[file]).return_value)

def test_get_all_drafts_for_user():
    """
    Tests that the service returns only messages of type DRAFT for the correct user.
    """
    drafts = services.get_all_drafts_for_user("test_user")
    assert len(drafts) == 2
    assert all(d.type == MessageType.DRAFT for d in drafts)
    assert all(d.user_id == "test_user" for d in drafts)
    assert {d.id for d in drafts} == {"draft-123", "draft-456"}

def test_get_all_drafts_for_unknown_user():
    """
    Tests that the service returns an empty list for a user with no drafts.
    """
    drafts = services.get_all_drafts_for_user("unknown_user")
    assert len(drafts) == 0

def test_delete_draft():
    """
    Tests that delete_draft removes the correct message and leaves others.
    """
    initial_count = len(services.MOCK_MESSAGES_DB)
    request = models.api_models.APIRejectDraftRequest(user_id="test_user", draft_message_id="draft-123")
    
    services.delete_draft(request)
    
    assert len(services.MOCK_MESSAGES_DB) == initial_count - 1
    assert "draft-123" not in [m.id for m in services.MOCK_MESSAGES_DB]

def test_delete_draft_wrong_user():
    """
    Tests that a user cannot delete another user's draft.
    """
    # In the current implementation, this will fail silently, which is fine for mock.
    initial_count = len(services.MOCK_MESSAGES_DB)
    request = models.api_models.APIRejectDraftRequest(user_id="wrong_user", draft_message_id="draft-123")
    
    services.delete_draft(request)
    
    assert len(services.MOCK_MESSAGES_DB) == initial_count

def test_process_thread_and_create_draft_with_new_messages(mocker, mock_prompts):
    """
    Tests the full process_thread_and_create_draft logic:
    - Finds new messages.
    - Deletes an old draft.
    - Stores the new messages.
    - Creates a new draft based on the full history.
    """
    # Arrange
    thread_name = "t1"
    # DB starts with one message and one draft for thread t1
    services.MOCK_MESSAGES_DB = [
        models.internal_models.InternalMessage(id="msg1", user_id="test_user", thread_name=thread_name, sender_name="Human", msg_content="First message", type=MessageType.MESSAGE),
        models.internal_models.InternalMessage(id="old_draft", user_id="test_user", thread_name=thread_name, sender_name="Agent", msg_content="Old draft", type=MessageType.DRAFT),
    ]
    initial_db_count = len(services.MOCK_MESSAGES_DB)

    mock_llm_response = "New mock LLM draft."
    mock_llm = mocker.patch("src.llm_client.get_llm_completion", return_value=mock_llm_response)
    
    # Request contains one old message and one new one
    request_messages = [
        models.api_models.APIMessage(message_id="msg1", sender_name="Human", date="2024-01-01", time="12:00", message_content="First message"),
        models.api_models.APIMessage(message_id="msg2", sender_name="Human", date="2024-01-01", time="12:01", message_content="Second message")
    ]
    request = models.api_models.APISendMessageRequest(user_id="test_user", thread_name=thread_name, messages=request_messages)

    # Act
    new_draft_id = services.process_thread_and_create_draft(request)

    # Assert
    # Old draft was removed, new message and new draft were added (+2, -1 = +1)
    assert len(services.MOCK_MESSAGES_DB) == initial_db_count + 1
    assert "old_draft" not in [m.id for m in services.MOCK_MESSAGES_DB]
    assert "msg2" in [m.id for m in services.MOCK_MESSAGES_DB]
    
    # Assert LLM was called with the full history
    llm_call_args = mock_llm.call_args[0][0]
    assert "First message" in llm_call_args[1]["content"]
    assert "Second message" in llm_call_args[2]["content"]

    # Assert new draft is correct
    new_draft = next((m for m in services.MOCK_MESSAGES_DB if m.id == new_draft_id), None)
    assert new_draft is not None
    assert new_draft.msg_content == mock_llm_response
    assert new_draft.type == MessageType.DRAFT

def test_create_revised_draft_from_feedback(mocker, mock_prompts):
    """
    Tests that a new draft is created and the agent context is stored,
    while the old draft is deleted.
    """
    # Arrange
    # Clear agent DB for this test
    services.MOCK_AGENTS_DB.clear()
    
    mock_llm_response = "Mock LLM revised draft."
    mock_llm = mocker.patch("src.llm_client.get_llm_completion", return_value=mock_llm_response)
    
    old_draft_id = "draft-123"
    initial_db_count = len(services.MOCK_MESSAGES_DB)
    request = models.api_models.APIProcessFeedbackRequest(user_id="test_user", draft_message_id=old_draft_id, feedback="Make it better.")

    # Act
    services.create_revised_draft_from_feedback(request)

    # Assert
    # DB count should be unchanged (1 draft deleted, 1 draft added)
    assert len(services.MOCK_MESSAGES_DB) == initial_db_count
    # Old draft should be gone
    assert old_draft_id not in [m.id for m in services.MOCK_MESSAGES_DB]
    
    # A new draft should exist with the revised content
    new_draft = next((m for m in services.MOCK_MESSAGES_DB if m.msg_content == mock_llm_response), None)
    assert new_draft is not None
    assert new_draft.type == MessageType.DRAFT
    
    # Agent context should be stored
    assert len(services.MOCK_AGENTS_DB) == 1
    new_agent_id = str(new_draft.agent_id)
    assert new_agent_id is not None
    assert new_agent_id in services.MOCK_AGENTS_DB
    assert services.MOCK_AGENTS_DB[new_agent_id] == mock_llm.call_args[0][0] 