import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from api.main import app
import datetime

# Use a fixture to manage the client's lifespan
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_send_messages(mocker, client):
    # Mock the background task function
    mock_task = mocker.patch("api.background_tasks.run_thread_processing")
    
    payload = {
        "user_id": "test_user",
        "thread_name": "test_thread",
        "messages": [
            {
                "message_id": "msg1",
                "sender_name": "sender1",
                "date": str(datetime.datetime.now().date()),
                "time": str(datetime.datetime.now().time()),
                "message_content": "Hello world"
            }
        ]
    }
    response = client.post("/send-messages/", json=payload)
    assert response.status_code == 202
    assert response.json() == {"message": "Message processing started in the background"}
    mock_task.assert_called_once()

def test_process_feedback(mocker, client):
    # Mock the background task function
    mock_task = mocker.patch("api.background_tasks.run_feedback_processing")
    
    payload = {
        "user_id": "test_user",
        "draft_message_id": "draft123",
        "feedback": "This is great!"
    }
    response = client.post("/process-feedback/", json=payload)
    assert response.status_code == 202
    assert response.json() == {"message": "Feedback processing started in the background"}
    mock_task.assert_called_once()

@pytest.mark.asyncio
async def test_reject_draft(mocker, client):
    # Mock the async delete_draft function
    mock_delete = mocker.patch("api.app_services.delete_draft", new_callable=AsyncMock)
    
    payload = {
        "user_id": "test_user",
        "draft_message_id": "draft123"
    }
    response = client.post("/reject-draft/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Draft rejected"}
    mock_delete.assert_called_once()

@pytest.mark.asyncio
async def test_get_draft_messages(mocker, client):
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
    mock_get_drafts = mocker.patch("api.app_services.get_all_drafts_for_user", new_callable=AsyncMock)
    mock_get_drafts.return_value = [
        type('Draft', (), {
            'thread_name': d['thread_name'],
            'id': d['draft_message_id'],
            'msg_content': d['draft_message_content'],
            'to_api_draft_message': lambda self=d, d=d: d
        })()
        for d in mock_drafts
    ]
    
    response = client.get("/draft-messages/?user_id=test_user")
    assert response.status_code == 200
    response_data = response.json()
    assert "draft_messages" in response_data
    assert response_data["draft_messages"] == mock_drafts
    mock_get_drafts.assert_called_once_with("test_user") 