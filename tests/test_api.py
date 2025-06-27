import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from api.main import app
import datetime

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_send_messages(mocker):
    # Mock the background task function
    mock_task = mocker.patch("src.background_tasks.run_thread_processing")

    payload = {
        "user_id": "test_user",
        "thread_name": "test_thread",
        "messages": [
            {
                "message_id": "msg1",
                "sender_name": "sender1",
                "date": str(datetime.date.today()),
                "time": str(datetime.time(12, 30)),
                "message_content": "Hello world"
            }
        ]
    }
    response = client.post("/send-messages/", json=payload)
    assert response.status_code == 202
    assert response.json() == {"message": "Message processing started in the background"}
    # Assert that the task was called once
    mock_task.assert_called_once()

def test_process_feedback(mocker):
    # Mock the background task function
    mock_task = mocker.patch("src.background_tasks.run_feedback_processing")

    payload = {
        "user_id": "test_user",
        "draft_message_id": "draft123",
        "feedback": "This is great!"
    }
    response = client.post("/process-feedback/", json=payload)
    assert response.status_code == 202
    assert response.json() == {"message": "Feedback processing started in the background"}
    # Assert that the task was called once
    mock_task.assert_called_once()

def test_reject_draft(mocker):
    # Mock the async delete_draft function
    mock_delete = AsyncMock()
    mocker.patch("src.app_services.delete_draft", mock_delete)

    payload = {
        "user_id": "test_user",
        "draft_message_id": "draft123"
    }
    response = client.post("/reject-draft/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Draft rejected"}
    # Assert that the async function was called
    mock_delete.assert_called_once()

def test_get_draft_messages(mocker):
    # Mock the async get_all_drafts_for_user function to return test drafts
    mock_drafts = [
        {
            "thread_name": "Arthur Stockman",
            "draft_message_id": "draft-123",
            "draft_message_content": "This is a draft message."
        },
        {
            "thread_name": "Lotte Verheyden",
            "draft_message_id": "draft-456",
            "draft_message_content": "This is another draft message."
        }
    ]
    
    # Create a mock that can be awaited and returns the test drafts
    mock_get_drafts = AsyncMock(return_value=[
        type('Draft', (), {
            'thread_name': d['thread_name'],
            'id': d['draft_message_id'],
            'msg_content': d['draft_message_content'],
            'to_api_draft_message': lambda self=None: d
        })()
        for d in mock_drafts
    ])
    mocker.patch("src.app_services.get_all_drafts_for_user", mock_get_drafts)

    response = client.get("/draft-messages/?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "draft_messages" in data
    assert isinstance(data["draft_messages"], list)
    assert len(data["draft_messages"]) == 2
    # Check structure of the first draft
    draft = data["draft_messages"][0]
    assert "thread_name" in draft
    assert "draft_message_id" in draft
    assert "draft_message_content" in draft 